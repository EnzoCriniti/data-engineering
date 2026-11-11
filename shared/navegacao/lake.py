"""Ingestão HDFS, migração e publicação do funil Delta da NuvemStore."""

import argparse
from contextlib import contextmanager
from datetime import datetime, time, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from delta.tables import DeltaTable
from pyspark.sql import SparkSession, functions as F

from events import normalize, raw_events
from generate import COORTE, PEDIDOS_DEMO, fixture
from migration import Divergencia, canonical_json, publish, read_snapshot, reconcile, snapshot_hash, write_snapshot


ORDER_SCHEMA = "pedido_id bigint, cliente_id bigint, status string"
SQL = Path(__file__).with_name("funil.sql")
HDFS = "hdfs://namenode:9000/navegacao"
PASSOS = ("visualizaram", "adicionaram", "iniciaram", "compraram")


class ObjectStore:
    def __init__(self):
        self.bucket = os.environ["LAKE_BUCKET"]
        self.uri = f"s3a://{self.bucket}/navegacao"
        self.revision = os.getenv("LAKE_REVISION", "local")
        self.s3 = boto3.client(
            "s3", endpoint_url=os.environ["S3_ENDPOINT"], region_name="us-east-1",
            config=Config(s3={"addressing_style": "path"}, request_checksum_calculation="when_required"),
        )
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError as error:
            if error.response["Error"]["Code"] not in ("404", "NoSuchBucket"):
                raise
            self.s3.create_bucket(Bucket=self.bucket)

    def read_optional(self, key):
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=f"navegacao/{key}")
        except self.s3.exceptions.NoSuchKey:
            return None
        with response["Body"] as body:
            return json.load(body)

    def put(self, key, value):
        self.s3.put_object(
            Bucket=self.bucket, Key=f"navegacao/{key}",
            Body=(canonical_json(value) + "\n").encode(), ContentType="application/json",
        )

    def manifests(self):
        pages = self.s3.get_paginator("list_objects_v2").paginate(
            Bucket=self.bucket, Prefix="navegacao/manifestos/"
        )
        keys = sorted(entry["Key"] for page in pages for entry in page.get("Contents", []))
        return [self.read_optional(key.removeprefix("navegacao/")) for key in keys]


@contextmanager
def one_writer():
    with open("/lock/navegacao.lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def spark_session():
    builder = (
        SparkSession.builder.appName("NuvemStore Navegação")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "2")
        .config("spark.sql.sources.partitionColumnTypeInference.enabled", "false")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.databricks.delta.snapshotPartitions", "4")
        .config("spark.ui.enabled", "false")
    )
    if "S3_ENDPOINT" in os.environ:
        endpoint = os.environ["S3_ENDPOINT"]
        builder = (
            builder.config("spark.hadoop.fs.s3a.endpoint", endpoint)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", str(endpoint.startswith("https:")).lower())
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.EnvironmentVariableCredentialsProvider")
        )
    return builder.getOrCreate()


def sample_orders(spark):
    if not os.getenv("OLTP_HOST"):
        return PEDIDOS_DEMO
    query = "SELECT pedido_id::bigint, cliente_id::bigint, status FROM pedido WHERE status = 'pago' ORDER BY pedido_id LIMIT 2"
    rows = (
        spark.read.format("jdbc")
        .option("driver", "org.postgresql.Driver")
        .option("url", f"jdbc:postgresql://{os.environ['OLTP_HOST']}:5432/nuvemstore")
        .option("user", os.getenv("OLTP_USER", "nuvemstore"))
        .option("password", os.environ["OLTP_PASSWORD"])
        .option("query", query)
        .load()
        .orderBy("pedido_id")
        .collect()
    )
    if len(rows) != 2:
        raise ValueError("O PostgreSQL da fase 2 precisa de pelo menos dois pedidos pagos")
    return [tuple(row) for row in rows]


def source_snapshot(spark, lote, orders):
    return raw_events(spark, fixture(orders, lote)), spark.createDataFrame(orders, ORDER_SCHEMA)


def funnel(spark, silver):
    zone = ZoneInfo("America/Sao_Paulo")
    bounds = [int(datetime.combine(day, time.min, zone).timestamp()) for day in (COORTE, COORTE + timedelta(days=1))]
    spark.createDataFrame([tuple(bounds)], "inicio_s bigint, fim_s bigint").createOrReplaceTempView("parametros")
    silver.createOrReplaceTempView("silver_eventos")
    sessions = spark.sql(SQL.read_text(encoding="utf-8"))
    summary = sessions.agg(
        *(F.count(column).alias(step) for column, step in zip(
            ("visualizacao_seq", "carrinho_seq", "checkout_seq", "compra_seq"), PASSOS
        )),
        F.sort_array(F.collect_set("pedido_id")).alias("pedidos_convertidos"),
    ).withColumn("coorte", F.lit(COORTE.isoformat()))
    for previous, following in zip(PASSOS, PASSOS[1:]):
        loss = F.col(previous) - F.col(following)
        summary = summary.withColumn(f"abandono_{following}", loss).withColumn(
            f"taxa_abandono_{following}", F.when(F.col(previous) > 0, loss / F.col(previous))
        )
    return sessions, summary


def write_delta(spark, frame, uri, metadata):
    if DeltaTable.isDeltaTable(spark, uri):
        latest = DeltaTable.forPath(spark, uri).history(1).select("version", "userMetadata").first()
        if latest.userMetadata == metadata:
            return latest.version
    frame.write.format("delta").mode("overwrite").option("userMetadata", metadata).save(uri)
    return DeltaTable.forPath(spark, uri).history(1).select("version").first().version


def delta_gold(spark, store):
    manifests = store.manifests()
    if not manifests:
        raise ValueError("Nenhum lote publicado na bronze")
    snapshots = []
    for manifest in manifests:
        snapshot = read_snapshot(spark, manifest["destino"])
        if snapshot_hash(snapshot) != manifest["lote_sha256"]:
            raise Divergencia(f"Lote publicado foi alterado: {manifest['lote_sha256']}")
        snapshots.append(snapshot)
    raw, orders = snapshots[0]
    for next_raw, next_orders in snapshots[1:]:
        raw = raw.unionByName(next_raw)
        orders = orders.unionByName(next_orders)

    silver, quality = normalize(raw, orders)
    silver_uri = f"{store.uri}/silver/eventos"
    gold_uri = f"{store.uri}/gold/funil_diario"
    input_metadata = {
        "lotes": [m["lote_sha256"] for m in manifests],
        "coorte": COORTE.isoformat(),
        "revisao": store.revision,
    }
    code = hashlib.sha256()
    for filename in ("lake.py", "events.py", "migration.py", "evento-v1.schema.json", "funil.sql"):
        code.update(SQL.with_name(filename).read_bytes())
    input_metadata["codigo_sha256"] = code.hexdigest()

    silver_version = write_delta(spark, silver, silver_uri, canonical_json(input_metadata))
    fixed_silver = spark.read.format("delta").option("versionAsOf", silver_version).load(silver_uri)
    _, summary = funnel(spark, fixed_silver)
    metadata = {**input_metadata, "versao_silver": silver_version}
    gold_version = write_delta(spark, summary, gold_uri, canonical_json(metadata))
    persisted = spark.read.format("delta").option("versionAsOf", gold_version).load(gold_uri)
    result = {
        **metadata, **quality,
        "versao_gold": gold_version,
        "silver": silver_uri,
        "gold": gold_uri,
        "resultado": persisted.first().asDict(recursive=True),
    }
    store.put(f"provas/gold-{gold_version}.json", result)
    return result


def emit(value, artifact=None):
    report = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
    print(report, flush=True)
    if artifact and os.getenv("LAKE_ARTIFACTS"):
        output = Path(os.environ["LAKE_ARTIFACTS"])
        output.mkdir(parents=True, exist_ok=True)
        (output / artifact).write_text(report + "\n", encoding="utf-8")


def run(spark, args):
    source_uri = f"{HDFS}/{args.lote}"
    if args.command == "ingest":
        snapshot = source_snapshot(spark, args.lote, sample_orders(spark))
        hadoop = spark._jvm.org.apache.hadoop.fs.Path(source_uri)
        fs = hadoop.getFileSystem(spark._jsc.hadoopConfiguration())
        if fs.exists(hadoop):
            if snapshot_hash(read_snapshot(spark, source_uri)) != snapshot_hash(snapshot):
                raise Divergencia(f"Snapshot existente diverge: {source_uri}")
        else:
            candidate = f"{HDFS}/candidatos/{uuid4().hex}"
            write_snapshot(snapshot, candidate)
            if not fs.rename(spark._jvm.org.apache.hadoop.fs.Path(candidate), hadoop):
                raise IOError(f"Falha ao promover snapshot HDFS: {source_uri}")
        emit({"origem": source_uri, "linhas": snapshot[0].count(), "sha256": snapshot_hash(snapshot)})
        return

    store = ObjectStore()
    if args.command == "migrate":
        snapshot = read_snapshot(spark, source_uri)
        proof = publish(spark, store, snapshot, source_uri, funnel)
        emit(proof, f"reconciliacao-{args.lote}.json")
    elif args.command == "demo":
        manifests = store.manifests()
        if not manifests or args.lote == "tardio":
            if manifests:
                _, orders = read_snapshot(spark, manifests[0]["destino"])
                references = [tuple(row) for row in orders.orderBy("pedido_id").collect()]
            else:
                if args.lote == "tardio":
                    raise ValueError("Publique o lote base antes do lote tardio")
                references = sample_orders(spark)
            snapshot = source_snapshot(spark, args.lote, references)
            publish(spark, store, snapshot, f"fixture://navegacao/{args.lote}", funnel)
        emit(delta_gold(spark, store), "gold.json")
    elif args.command == "build":
        emit(delta_gold(spark, store), "gold.json")
    elif args.command == "history":
        uri = f"{store.uri}/gold/funil_diario"
        history = DeltaTable.forPath(spark, uri).history(2).orderBy(F.desc("version")).collect()
        if len(history) < 2:
            raise ValueError("Publique dois lotes para consultar a versão anterior")
        previous = history[1].version
        result = spark.read.format("delta").option("versionAsOf", previous).load(uri).first()
        emit({
            "versao_anterior": previous, "resultado_anterior": result.asDict(recursive=True),
            "historico": [{"versao": row.version, "operacao": row.operation} for row in history],
        }, "historico.json")
    elif args.command == "test":
        from integration import verify

        verify(spark, store, source_uri, funnel, delta_gold, emit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["ingest", "migrate", "demo", "build", "history", "test"])
    parser.add_argument("--lote", choices=["base", "tardio"], default="base")
    args = parser.parse_args()
    with one_writer():
        spark = spark_session()
        try:
            run(spark, args)
        finally:
            spark.stop()


if __name__ == "__main__":
    main()

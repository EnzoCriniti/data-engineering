import hashlib
import json
from uuid import uuid4

from pyspark.sql import functions as F

from events import normalize


class Divergencia(ValueError):
    pass


def read_snapshot(spark, uri):
    return (
        spark.read.parquet(f"{uri}/eventos").select("raw_json", "dt_evento"),
        spark.read.parquet(f"{uri}/pedidos").select("pedido_id", "cliente_id", "status"),
    )


def write_snapshot(snapshot, uri):
    raw, orders = snapshot
    raw.write.mode("error").partitionBy("dt_evento").parquet(f"{uri}/eventos")
    orders.write.mode("error").parquet(f"{uri}/pedidos")


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def snapshot_hash(snapshot):
    digest = hashlib.sha256()
    for frame in snapshot:
        digest.update((canonical_json(frame.dtypes) + "\n").encode())
        for row in frame.orderBy(*frame.columns).toLocalIterator():
            digest.update((canonical_json(row.asDict()) + "\n").encode())
    return digest.hexdigest()


def compare(label, left, right):
    if left.dtypes != right.dtypes:
        raise Divergencia(f"{label}: tipos ou colunas diferentes")
    if left.exceptAll(right).take(1) or right.exceptAll(left).take(1):
        raise Divergencia(f"{label}: conteúdo diferente (EXCEPT ALL)")


def partition_stats(raw):
    rows = raw.select(
        "dt_evento",
        F.get_json_object("raw_json", "$.event_id").alias("event_id"),
        F.get_json_object("raw_json", "$.event_ts").alias("event_ts"),
    )
    return [
        row.asDict()
        for row in rows.groupBy("dt_evento").agg(
            F.count("*").alias("linhas"),
            F.countDistinct("event_id").alias("ids_distintos"),
            (F.count("event_id") - F.countDistinct("event_id")).alias("repeticoes_de_id"),
            F.min("event_ts").alias("primeiro_ts"),
            F.max("event_ts").alias("ultimo_ts"),
        ).orderBy("dt_evento").collect()
    ]


def reconcile(spark, source, target, funnel):
    compare("eventos", source[0], target[0])
    compare("pedidos", source[1], target[1])
    left, _ = normalize(*source)
    right, _ = normalize(*target)
    left_sessions, left_summary = funnel(spark, left)
    right_sessions, right_summary = funnel(spark, right)
    compare("funil por sessão", left_sessions, right_sessions)
    compare("funil diário", left_summary, right_summary)
    return {
        "particoes_origem": partition_stats(source[0]),
        "particoes_destino": partition_stats(target[0]),
        "schema_eventos": source[0].dtypes,
        "schema_pedidos": source[1].dtypes,
        "linhas_pedidos": source[1].count(),
        "funil_origem": left_summary.first().asDict(recursive=True),
        "funil_destino": right_summary.first().asDict(recursive=True),
        "except_all_origem_destino": 0,
        "except_all_destino_origem": 0,
    }


def publish(spark, store, snapshot, source_uri, funnel):
    batch = snapshot_hash(snapshot)
    key = f"manifestos/{batch}.json"
    previous = store.read_optional(key)
    if previous is not None:
        target = read_snapshot(spark, previous["destino"])
        if snapshot_hash(target) != batch:
            raise Divergencia(f"Lote publicado foi alterado: {batch}")
        # A prova depende da origem. Uma carga direta anterior não prova a migração de HDFS.
        if previous["origem"] == source_uri:
            return previous
        destination = previous["destino"]
    else:
        destination = f"{store.uri}/bronze/candidatos/{batch}/{uuid4().hex}"
        write_snapshot(snapshot, destination)
        target = read_snapshot(spark, destination)

    proof = reconcile(spark, snapshot, target, funnel)
    manifest = {
        **proof,
        "lote_sha256": batch,
        "origem": source_uri,
        "destino": destination,
        "revisao": store.revision,
    }
    if previous is None:
        store.put(key, manifest)
    return manifest

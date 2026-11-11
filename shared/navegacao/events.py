import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from pyspark.sql import Window, functions as F


SCHEMA = Path(__file__).with_name("evento-v1.schema.json")
EVENT_FIELDS = (
    "event_id", "session_id", "event_seq", "event_type",
    "event_epoch_s", "produto_id", "pedido_id", "cliente_id",
)


@lru_cache(maxsize=1)
def validator():
    return Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def parse(raw):
    try:
        event = json.loads(raw)
        if not validator().is_valid(event):
            return (None,) * 8 + ("contrato",)
        instant = datetime.fromisoformat(event["event_ts"].replace("Z", "+00:00"))
        values = (
            event["event_id"], event["session_id"], int(event["event_seq"]),
            event["event_type"], int(instant.timestamp()),
            *(int(event[key]) if key in event else None for key in ("produto_id", "pedido_id", "cliente_id")),
        )
        if any(value is not None and value >= 2**63 for value in (values[2], *values[5:])):
            return (None,) * 8 + ("fora_da_faixa",)
        return values + (None,)
    except (ValueError, OverflowError):
        return (None,) * 8 + ("json_ou_timestamp",)


parse_event = F.udf(
    parse,
    "struct<event_id:string,session_id:string,event_seq:bigint,event_type:string,"
    "event_epoch_s:bigint,produto_id:bigint,pedido_id:bigint,cliente_id:bigint,erro:string>",
)


def raw_events(spark, lines):
    return (
        spark.createDataFrame([(line,) for line in lines], "raw_json string")
        .withColumn("event_epoch_s", parse_event("raw_json").event_epoch_s)
        .select(
            "raw_json",
            F.coalesce(F.from_unixtime("event_epoch_s", "yyyy-MM-dd"), F.lit("invalido")).alias("dt_evento"),
        )
    )


def normalize(raw, orders):
    parsed = raw.select(parse_event("raw_json").alias("evento")).select("evento.*").cache()
    try:
        invalid = parsed.filter("erro IS NOT NULL").count()
        accepted = parsed.filter("erro IS NULL").select(*EVENT_FIELDS)
        events = accepted.distinct().cache()
        try:
            duplicates = accepted.count() - events.count()
            for key in [("event_id",), ("session_id", "event_seq")]:
                if events.groupBy(*key).count().filter("count > 1").take(1):
                    raise ValueError(f"Identidade conflitante: {key}")
            ordered = Window.partitionBy("session_id").orderBy("event_seq")
            if events.withColumn("anterior", F.lag("event_epoch_s").over(ordered)).filter(
                "event_epoch_s < anterior"
            ).take(1):
                raise ValueError("Timestamp retrocedeu na sequência da sessão")
            orders = orders.distinct()
            if orders.groupBy("pedido_id").count().filter("count > 1").take(1):
                raise ValueError("Snapshot contém vínculos conflitantes para o mesmo pedido")

            e, p = events.alias("e"), orders.alias("p")
            eligible = (
                (F.col("e.event_type") == "purchase_completed")
                & (F.col("e.pedido_id") == F.col("p.pedido_id"))
                & (F.col("p.status") == "pago")
                & (F.col("e.cliente_id").isNull() | (F.col("e.cliente_id") == F.col("p.cliente_id")))
            )
            silver = e.join(p, eligible, "left").select("e.*", F.col("p.pedido_id").alias("pedido_confirmado_id"))
            return silver, {"invalidos": invalid, "retries_deduplicados": duplicates}
        finally:
            events.unpersist()
    finally:
        parsed.unpersist()

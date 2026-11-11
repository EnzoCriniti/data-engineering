"""Aceite do estudo HDFS, da publicação MinIO e do histórico Delta."""

from pyspark.sql import functions as F

from migration import Divergencia, read_snapshot, reconcile, write_snapshot


STEPS = ("visualizaram", "adicionaram", "iniciaram", "compraram")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify(spark, store, source_uri, funnel, delta_gold, emit):
    before = store.manifests()
    require(len(before) == 1 and before[0]["origem"] == source_uri, "Esperado um lote base migrado de HDFS")
    raw, orders = read_snapshot(spark, source_uri)
    target = f"{store.uri}/testes/divergente"
    # Mudança com contagens preservadas. O candidato fica fora do registro de lotes.
    altered = raw.withColumn(
        "raw_json",
        F.when(F.col("dt_evento") == "invalido", F.lit("{}")).otherwise(F.col("raw_json")),
    )
    write_snapshot((altered, orders), target)
    try:
        reconcile(spark, (raw, orders), read_snapshot(spark, target), funnel)
    except Divergencia as error:
        emit({"candidato_rejeitado": target, "motivo": str(error)}, "divergencia.json")
    else:
        raise AssertionError("A migração aceitou conteúdo divergente")
    require(store.manifests() == before, "O teste de divergência alterou os manifestos publicados")

    result = delta_gold(spark, store)
    values = result["resultado"]
    ids = [row.pedido_id for row in orders.orderBy("pedido_id").collect()]
    require(tuple(values[step] for step in STEPS) == (4, 3, 2, 1), f"Funil incorreto: {values}")
    require(values["pedidos_convertidos"] == ids[:1], "Conversão sem vínculo com o primeiro pedido pago")
    require(values["taxa_abandono_compraram"] == 0.5, "Taxa de abandono no checkout incorreta")
    require(result["invalidos"] == 1 and result["retries_deduplicados"] == 1, "Qualidade da silver incorreta")
    require(delta_gold(spark, store) == result, "O replay alterou dados ou versões Delta")
    emit(result, "gold-base.json")

# Capítulo 10 — Lakehouse + Medallion 🟡

> **De onde viemos:** no [cap. 09](../09-migracao-hdfs-para-s3) movemos o lake para object storage barato e elástico. Mas arquivos soltos no S3 não garantem transações, schema enforcement nem time travel. O lakehouse traz a confiabilidade do warehouse sobre o storage barato do lake.

## Cenário de negócio

A NuvemStore passou a depender do lake para decisões. Um job parcial ou uma escrita concorrente pode deixar dados inconsistentes e afetar dashboards. Sem transações, "leu no meio de uma escrita" vira número errado num relatório.

O lakehouse entra para dar garantias de warehouse (ACID, schema, histórico) sobre o object storage do cap. 09, organizando o dado em camadas de qualidade crescente — a arquitetura **Medallion**.

## O que esta etapa mostra

Uma camada transacional (Delta Lake) sobre o S3/MinIO, processada por Spark e consultada por Trino, organizada em três níveis:

```text
bronze  -> dado cru, fiel à origem (ingestão sem transformar)
silver  -> tipado, deduplicado, regras técnicas aplicadas
gold    -> métricas de negócio, equivalentes aos marts anteriores
```

## Conceitos

**Lakehouse.** Une o melhor dos dois mundos: storage barato e aberto do lake + garantias transacionais do warehouse. Não é um produto, é um padrão habilitado por formatos como Delta Lake e Iceberg.

**Delta Lake e o `_delta_log`.** O Delta mantém um log de transações (`_delta_log`) ao lado dos Parquet. Esse log é o que dá ACID, schema enforcement e time travel sobre arquivos imutáveis. É distinto do metastore/catálogo: o log descreve o estado da tabela; o catálogo só diz "esta tabela existe e fica aqui".

**Medallion (bronze/silver/gold).** Camadas de refinamento progressivo. Bronze preserva fidelidade à origem; silver limpa e tipa; gold entrega métricas prontas para consumo. Cada camada é um contrato claro de qualidade.

**MERGE, schema enforcement e time travel.** `MERGE` faz upsert idempotente (chave da CDC do cap. 11). Schema enforcement rejeita escrita fora do esquema. Time travel consulta versões antigas da tabela — auditoria e rollback.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe MinIO, Spark, Airflow, Trino, metastore e Metabase. Os jobs Delta (`bronze.py`, `silver.py`, `gold.py`) e os catálogos Trino são o roteiro de construção descrito no BUILD.

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o ambiente lakehouse e acessar as UIs.
- **[BUILD.md](./BUILD.md)** — o roteiro Medallion: bronze→silver→gold em Delta, registro no catálogo e a equivalência gold vs marts anteriores.

## A dor que sobra

Mesmo confiável, o lakehouse ainda é batch. Para reduzir a latência, a próxima dor é capturar mudanças continuamente, direto do banco. → [Capítulo 11: CDC com Debezium](../11-cdc-com-debezium).

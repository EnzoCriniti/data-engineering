# Runbook — Capítulo 09: migração de HDFS para S3

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — HDFS, MinIO, Spark, Trino, Airflow e Metabase sobem prontos; os jobs de migração e federação ainda serão implementados (ver [GUIDE.md](./GUIDE.md) para o passo-a-passo e [SOLUTION.md](./SOLUTION.md) para o código).

## O que este capítulo entrega hoje

O ambiente híbrido para simular a migração: o lake legado em HDFS, o alvo moderno em MinIO (S3-compatible), Spark para mover dados, Trino para federar consultas, Airflow para orquestrar e Metabase para o BI.

## Pré-requisitos

- Docker e Docker Compose, com memória generosa (vários serviços pesados).
- Portas livres: `9870` (HDFS), `9000`/`9001` (MinIO API/console), `8090` (Spark), `8080` (Airflow), `8085` (Trino) — confira os valores no `.env.example`.

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

UIs típicas:

```text
HDFS NameNode:  http://localhost:9870
MinIO console:  http://localhost:9001
Spark master:   http://localhost:8090
Airflow:        http://localhost:8080
```

## Conferir

```bash
# HDFS no ar
docker compose exec namenode hdfs dfs -ls /

# MinIO respondendo (via cliente mc dentro do container, quando configurado)
docker compose exec minio mc ls local/
```

## Quando os jobs estiverem implementados

```bash
# migrar partições frias de HDFS para S3/MinIO (job Spark)
docker compose run spark-submit spark-submit /app/jobs/migrate_hdfs_to_s3.py
```

A **consulta federada** (HDFS + S3 ao mesmo tempo) não é um job Spark: é feita pelo Trino, usando o catálogo `trino/catalog/hive.properties`. Com a partição migrada, o mesmo `SELECT` continua respondendo esteja o dado em HDFS ou em S3:

```sql
SELECT count(*) FROM hive.default.entregas;   -- via Trino, transparente ao usuário
```

**Validação:** as contagens por partição devem bater antes e depois da migração (reconciliação — o próprio `migrate_hdfs_to_s3.py` imprime essa checagem), e o Trino deve retornar o mesmo resultado independentemente de onde a partição está.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 10](../10-lakehouse-medallion): dar ao lake em object storage as garantias transacionais do warehouse, com Delta/Iceberg e a arquitetura Medallion.

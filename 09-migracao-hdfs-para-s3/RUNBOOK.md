# Runbook — Capítulo 09: migração de HDFS para S3

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — HDFS, MinIO, Spark, Trino, Airflow e Metabase sobem prontos; os jobs de migração e federação ainda serão implementados (ver [BUILD.md](./BUILD.md)).

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
# migrar partições frias de HDFS para S3/MinIO
docker compose exec spark-master spark-submit /opt/jobs/migrate_hdfs_to_s3.py
# consulta federada cobrindo HDFS + S3
docker compose exec spark-master spark-submit /opt/jobs/query_federada.py
# aplicar política de tiering quente/frio
docker compose exec spark-master spark-submit /opt/jobs/tiering.py
```

**Validação:** as contagens por partição devem bater antes e depois da migração (reconciliação), e o Trino deve retornar o mesmo resultado consultando a partição esteja ela em HDFS ou em S3.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 10](../10-lakehouse-medallion): dar ao lake em object storage as garantias transacionais do warehouse, com Delta/Iceberg e a arquitetura Medallion.

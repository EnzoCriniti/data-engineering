# Runbook — Capítulo 08: Data Lake com HDFS e Spark

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — HDFS, Spark e Hive Metastore sobem prontos; os jobs Spark de ingestão/curadoria ainda serão implementados (ver [BUILD.md](./BUILD.md)).

## O que este capítulo entrega hoje

Um data lake distribuído em modo local: HDFS (namenode + datanode), cluster Spark (master + worker) e o Hive Metastore como catálogo, prontos para receber jobs.

## Pré-requisitos

- Docker e Docker Compose.
- Memória suficiente para o cluster (Spark + HDFS são pesados; recomenda-se 8 GB+ disponíveis ao Docker).
- Portas `9870` (HDFS NameNode) e `8090` (Spark master) livres.

## Subir o lake

```bash
cp .env.example .env
docker compose up -d
```

UIs:

```text
HDFS NameNode:  http://localhost:9870
Spark master:   http://localhost:8090
```

Na UI do HDFS você confere os datanodes vivos e o uso de capacidade; na do Spark, os workers registrados e os jobs em execução.

## Conferir o cluster

```bash
# datanodes vivos e relatório do HDFS
docker compose exec namenode hdfs dfsadmin -report

# listar a raiz do HDFS
docker compose exec namenode hdfs dfs -ls /
```

## Quando os jobs estiverem implementados

```bash
# submeter um job ao cluster Spark
docker compose exec spark-master spark-submit /opt/jobs/ingest_raw.py
docker compose exec spark-master spark-submit /opt/jobs/build_curated.py
```

**Validação:** após a curadoria, os Parquet devem aparecer no HDFS (`hdfs dfs -ls /curated/...`) e os datasets registrados no metastore.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 09](../09-migracao-hdfs-para-s3): migrar o storage de HDFS para S3/MinIO, desacoplando storage e compute.

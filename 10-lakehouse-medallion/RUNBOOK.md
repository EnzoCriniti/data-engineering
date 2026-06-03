# Runbook — Capítulo 10: Lakehouse + Medallion

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — MinIO, Spark, Trino, Airflow, metastore e Metabase sobem prontos; os jobs Delta (bronze/silver/gold) ainda serão implementados (ver [BUILD.md](./BUILD.md)).

## O que este capítulo entrega hoje

O ambiente lakehouse: object storage (MinIO), Spark com Delta Lake, Trino para consulta, metastore para catálogo, Airflow para orquestração e Metabase para BI.

## Pré-requisitos

- Docker e Docker Compose, com memória generosa.
- Portas livres: `9000`/`9001` (MinIO), `8090` (Spark), `8085` (Trino), `8080` (Airflow), mais a do Metabase — confira no `.env.example`.

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

UIs típicas:

```text
MinIO console:  http://localhost:9001
Spark master:   http://localhost:8090
Airflow:        http://localhost:8080
```

## Quando os jobs estiverem implementados

```bash
docker compose exec spark-master spark-submit /opt/jobs/bronze.py
docker compose exec spark-master spark-submit /opt/jobs/silver.py
docker compose exec spark-master spark-submit /opt/jobs/gold.py
```

Consultar as camadas via Trino:

```sql
SELECT count(*) FROM lakehouse.bronze.eventos;
SELECT * FROM lakehouse.gold.receita_diaria LIMIT 10;
```

**Validação:** as métricas da camada gold devem ser equivalentes aos marts do warehouse dos capítulos anteriores antes de apontar o BI para o lakehouse.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 11](../11-cdc-com-debezium): capturar mudanças do banco em tempo quase real (CDC) para alimentar o lakehouse sem recarregar tudo.

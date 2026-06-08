# Runbook — Capítulo 07: orquestração com Airflow

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — os DAGs reais ainda serão implementados (ver [GUIDE.md](./GUIDE.md) para o passo-a-passo e [SOLUTION.md](./SOLUTION.md) para o código).

## O que este capítulo entrega hoje

O Airflow em modo `standalone`, pronto para receber DAGs.

## Pré-requisitos

- Docker e Docker Compose.
- Porta `8080` livre (Airflow). Para o BI, a porta definida no `.env`.

## Subir o Airflow

```bash
cp .env.example .env
docker compose up -d airflow
```

UI: `http://localhost:8080`. No modo standalone, a senha inicial aparece nos logs:

```bash
docker compose logs airflow | grep -i password
```

## BI opcional

```bash
docker compose --profile bi up -d metabase
```

## Quando os DAGs estiverem implementados

```bash
# colocar os DAGs em airflow/dags/ (já montado no container)
docker compose exec airflow airflow dags list
docker compose exec airflow airflow dags trigger nuvemstore_daily
# backfill de um intervalo
docker compose exec airflow airflow dags backfill nuvemstore_daily -s 2024-01-01 -e 2024-01-07
```

**Validação:** uma execução orquestrada deve produzir os mesmos marts que a execução manual dos capítulos anteriores.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d airflow
```

## Próximo passo

[Capítulo 08](../08-data-lake-com-spark): Data Lake com Spark para volume e dados semi-estruturados.

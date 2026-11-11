# Runbook — Snapshot de navegação no HDFS

## O que este capítulo entrega

Um snapshot de 16 linhas de NDJSON preservadas em Parquet, com duas datas UTC, uma linha inválida e o snapshot de dois pedidos de referência.

## Pré-requisitos

Python 3.11 ou superior para a fixture. Docker Compose v2 em Linux e acesso aos registries e ao Maven para o laboratório. Rode da raiz do repositório.

## Subir

```bash
compose=(docker compose -p nuvemstore-navegacao -f 10-lakehouse-medallion/docker-compose.yml --profile hdfs)
"${compose[@]}" up -d --wait namenode datanode
"${compose[@]}" build lakehouse
```

## Usar

```bash
python3 shared/navegacao/generate.py
"${compose[@]}" run --rm -T lakehouse ingest
```

A fixture local usa dois pedidos sintéticos de referência. O teste Linux do capítulo 10 prepara o PostgreSQL com o seeder da fase anterior e usa pedidos pagos desse banco.

## Validar

```bash
"${compose[@]}" exec -T namenode hdfs dfs -ls /navegacao/base/eventos
"${compose[@]}" run --rm -T lakehouse ingest
```

Esperado: `dt_evento=2026-11-10`, `dt_evento=2026-11-11`, `dt_evento=invalido`, e o mesmo SHA-256 e total de 16 linhas nas duas execuções.

## Recomeçar do zero

`"${compose[@]}" down -v` apaga os volumes descartáveis do projeto de estudo.

## Próximo passo

Preserve o snapshot e siga para a [reconciliação no MinIO](../09-migracao-hdfs-para-s3/RUNBOOK.md).

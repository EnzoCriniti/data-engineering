# Runbook — Equivalência HDFS → MinIO

## O que este capítulo entrega

O mesmo snapshot no HDFS e no MinIO, com `reconciliacao-base.json` e um manifesto do lote aceito em object storage.

## Pré-requisitos

Docker Compose v2 em Linux. Rode da raiz. Estes comandos recriam o snapshot do capítulo 08 quando necessário.

## Subir

```bash
compose=(docker compose -p nuvemstore-navegacao -f 10-lakehouse-medallion/docker-compose.yml --profile hdfs)
mkdir -p 10-lakehouse-medallion/data/evidencias
chmod a+w 10-lakehouse-medallion/data/evidencias
"${compose[@]}" up --build -d --wait namenode datanode minio
"${compose[@]}" build lakehouse
```

## Usar

```bash
"${compose[@]}" run --rm -T lakehouse ingest
"${compose[@]}" run --rm -T lakehouse migrate
```

## Validar

Abra `10-lakehouse-medallion/data/evidencias/reconciliacao-base.json`. Os dois `EXCEPT ALL` devem retornar zero diferenças. As partições devem somar 16 linhas de eventos e o funil deve resultar em `4 → 3 → 2 → 1` dos dois lados. O teste integrado cria um candidato adulterado e confirma a rejeição.

## Recomeçar do zero

`"${compose[@]}" down -v` apaga os volumes descartáveis do estudo. O script de ponta a ponta gera suas próprias evidências.

## Próximo passo

Consuma o manifesto já aprovado com o comando `build` do [capítulo 10](../10-lakehouse-medallion/RUNBOOK.md).

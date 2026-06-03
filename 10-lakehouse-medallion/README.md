# Capitulo 10 - Lakehouse + Medallion

> De onde viemos: o data lake guarda arquivos de forma barata e flexivel, mas arquivos soltos nao garantem transacoes, schema enforcement ou time travel.

## Cenario de negocio

A NuvemStore passou a depender do lake para decisoes. Um job parcial ou uma escrita concorrente pode deixar dados inconsistentes e afetar dashboards.

Lakehouse entra para trazer confiabilidade de warehouse sobre storage barato.

## Status desta etapa

Status atual: **ambiente base**.

O compose sobe:

- MinIO;
- Spark master e worker;
- Airflow;
- Trino;
- catalogo/metastore herdado do lake para registrar tabelas;
- Metabase.

Os jobs Delta (`bronze.py`, `silver.py`, `gold.py`) e os catalogos Trino serao implementados depois.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

## Conceitos principais

- Lakehouse.
- Delta Lake e `_delta_log`.
- diferenca entre transaction log e metastore/catalogo.
- ACID sobre object storage.
- Medallion: bronze, silver e gold.
- `MERGE`, schema enforcement e time travel.
- Query engine sobre lakehouse.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## Migracao esperada

Quando a integracao for implementada, este capitulo nao deve criar dados do zero. O fluxo esperado e migrar ou reprocessar dados que ja existem no warehouse/lake anterior, validar contagens e metricas, e entao reduzir a dependencia da camada antiga.

Plano de migracao:

1. ler os dados raw/curados ja migrados para S3/MinIO no capitulo 09;
2. recriar a camada bronze em Delta, preservando fidelidade a origem;
3. construir silver com tipagem, deduplicacao e regras tecnicas;
4. construir gold com metricas equivalentes aos marts anteriores;
5. registrar bronze, silver e gold no catalogo/metastore;
6. comparar gold vs marts/warehouse anteriores antes de apontar BI para o lakehouse;
7. manter a camada antiga apenas como fallback ate a validacao passar.

## A dor que sobra

Mesmo confiavel, o lakehouse ainda e batch. Para reduzir latencia, a proxima dor e capturar mudancas continuamente. Isso leva ao capitulo 11: CDC com Debezium.

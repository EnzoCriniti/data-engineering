# Capitulo 08 - Data Lake on-prem com HDFS

> De onde viemos: a plataforma ja tem OLTP, warehouse, dbt, API externa e Airflow. Agora o volume de dados semi-estruturados cresce e a empresa decide aproveitar infraestrutura on-prem existente para criar um data lake.

## Cenario de negocio

A NuvemStore recebe eventos de navegacao em JSON: page views, cliques, sessoes e interacoes com produtos. Carregar tudo direto em um warehouse relacional fica caro e rigido.

Como a empresa ja possui servidores on-prem, a primeira decisao e montar um lake em HDFS. Isso aproveita hardware existente e oferece data locality para jobs Spark, mas tambem cria acoplamento entre storage e compute.

## Status desta etapa

Status atual: **ambiente base**.

O compose sobe:

- HDFS namenode e datanode;
- Spark master e worker;
- Hive Metastore, como catalogo de tabelas/datasets do lake.

Os jobs de ingestao e curadoria (`ingest_raw.py`, `build_curated.py`) serao implementados depois.

## Como esta etapa migra a anterior

O data lake entra porque o warehouse nao e mais o melhor lugar para tudo. Ele recebe dados brutos e historicos que antes ficariam caros ou rigidos no warehouse.

Plano de migracao:

1. manter o warehouse para marts analiticos existentes;
2. carregar dados crus e historicos no HDFS;
3. usar Spark para converter JSON/CSV cru em Parquet curado;
4. registrar datasets no metastore;
5. comparar volumes e amostras contra origem/warehouse;
6. manter no warehouse apenas o que precisa ser servido como mart.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

HDFS NameNode:

```text
http://localhost:9870
```

UI do Spark master:

```text
http://localhost:8090
```

## Conceitos principais

- Data lake e schema-on-read.
- HDFS e data locality.
- Metastore/catalogo para registrar datasets.
- Spark como motor distribuido.
- JSON cru como entrada.
- Parquet como formato curado.
- Shuffle, particionamento, broadcast join e skew.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## A dor que sobra

O lake em HDFS funciona, mas operar storage on-prem fica rigido: storage e compute escalam juntos, a manutencao pesa, e a empresa quer elasticidade. Essa dor leva ao capitulo 09: migracao de HDFS para S3/MinIO.

# Build — Capítulo 09: como migrar de HDFS para S3

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Migrar o data lake legado de HDFS para object storage (S3/MinIO) de forma gradual, mantendo os consumidores funcionando durante a transição via federação de queries, e validando dados por partição.

## Pré-requisitos de conhecimento

- O lake HDFS do [cap. 08](../08-data-lake-com-spark) (raw/curated em Parquet, metastore).
- Object storage S3 (buckets, chaves, eventual consistency), Spark lendo/escrevendo `s3a://`.
- Trino como query engine federado (catálogos hive/HDFS e hive/S3).

## Estado inicial

Estado final do cap. 08: lake on-prem em HDFS funcional, com a dor de escalar storage e compute juntos. O alvo é o object storage.

## Passo 1 — Ambiente (`docker-compose.yml`)

HDFS (legado), MinIO (alvo S3), Spark (motor de migração), Trino (federação), Airflow (orquestração) e Metabase (BI). Montar `spark/jobs/`, `airflow/dags/` e `trino/catalog/`.

## Passo 2 — Inventário e classificação

Levantar partições/tabelas ainda no HDFS e classificá-las por criticidade e padrão de acesso (quente vs frio). Esse inventário é a base da decisão do que migrar primeiro — o frio/histórico vai antes, o quente fica por último.

## Passo 3 — Migração (`spark/jobs/migrate_hdfs_to_s3.py`)

Spark lê uma partição do HDFS (`hdfs://...`) e escreve em MinIO (`s3a://...`), preservando o formato Parquet e o esquema de particionamento. O job deve ser **idempotente por partição** (reescrever uma partição já migrada não duplica) e registrar a partição migrada num controle (tabela/manifesto).

## Passo 4 — Catálogos e federação Trino (`trino/catalog/`)

Configurar um catálogo apontando para o metastore com dados em HDFS e outro com dados em S3 (ou um único catálogo com `LOCATION` por tabela). `query_federada.py` valida que a mesma consulta lógica cobre as duas zonas, escondendo do consumidor onde está cada partição.

## Passo 5 — Tiering (`spark/jobs/tiering.py`)

Política que move partições de quente (HDFS) para frio (S3) conforme idade/acesso, orquestrada por uma DAG Airflow. Reduz custo mantendo o que é sensível perto do compute durante a transição.

## Passo 6 — Reconciliação

Antes e depois de cada migração, comparar `count(*)` e amostras por partição entre origem (HDFS) e destino (S3). Só marcar a partição como migrada quando as contagens baterem.

## Validações (definição de pronto)

- [ ] `migrate_hdfs_to_s3.py` move uma partição de HDFS para MinIO sem duplicar ao reprocessar.
- [ ] Trino consulta a mesma tabela esteja a partição em HDFS ou S3, com resultado idêntico.
- [ ] Reconciliação por partição (contagem + amostra) passa.
- [ ] A DAG de tiering move partições frias automaticamente.

## Estado final (gabarito para o próximo capítulo)

Storage migrado para object storage, compute desacoplado, consumidores intactos. Falta dar ao lake garantias transacionais (ACID, schema enforcement, time travel) — gancho para o [cap. 10: Lakehouse Medallion](../10-lakehouse-medallion).

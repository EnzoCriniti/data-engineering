# Build — Capítulo 08: como construir o Data Lake com HDFS e Spark

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação dos jobs. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Montar um data lake on-prem em HDFS e usar Spark para transformar eventos JSON crus em Parquet curado, registrado no Hive Metastore — sem trazer esse volume para o warehouse relacional.

## Pré-requisitos de conhecimento

- HDFS (blocos, replicação, data locality), Spark (DataFrame, lazy evaluation, shuffle), Parquet (colunar).
- Schema-on-read vs schema-on-write.
- O warehouse do [cap. 03](../03-warehouse-dedicado) como destino servido (marts), agora complementado pelo lake.

## Estado inicial

Estado final do [cap. 07](../07-orquestracao-com-airflow): pipeline batch orquestrado, com warehouse e marts. Falta um lugar barato e elástico para dados de alto volume e baixo valor por linha (eventos de navegação).

## Passo 1 — Ambiente (`docker-compose.yml`)

HDFS (namenode + datanode), Spark (master + worker) e Hive Metastore (com um Postgres de backend para o metastore). Montar uma pasta de jobs (`spark/jobs/`) no Spark master como `/opt/jobs`.

## Passo 2 — Ingestão crua (`spark/jobs/ingest_raw.py`)

Ler os eventos JSON e gravá-los no HDFS na camada `raw`, **sem transformar** (schema-on-read). Particionar por data de evento (`/raw/eventos/dt=YYYY-MM-DD/`) para podar leituras futuras. A camada raw é o contrato: o dado bruto fica preservado e auditável.

## Passo 3 — Curadoria (`spark/jobs/build_curated.py`)

Ler o raw, aplicar schema explícito (não inferido), limpar e tipar, e gravar **Parquet** particionado na camada `curated`. Registrar a tabela no metastore (`CREATE TABLE ... USING parquet LOCATION ...` ou via `saveAsTable`). Decisões de performance: definir o número de partições de saída, evitar arquivos pequenos (coalesce), e usar broadcast join quando uma das tabelas é pequena.

## Passo 4 — Plano de migração desde o warehouse

O lake não substitui o warehouse; redistribui responsabilidades:

1. manter no warehouse os marts analíticos já servidos;
2. carregar dados crus e históricos de alto volume no HDFS;
3. converter JSON/CSV cru em Parquet curado com Spark;
4. registrar os datasets no metastore;
5. comparar volumes e amostras contra origem/warehouse (reconciliação);
6. manter no warehouse apenas o que precisa ser servido como mart.

## Validações (definição de pronto)

- [ ] `ingest_raw.py` grava o raw particionado por data no HDFS.
- [ ] `build_curated.py` produz Parquet curado e registra a tabela no metastore.
- [ ] Uma query Spark sobre a tabela curada retorna contagens coerentes com o raw.
- [ ] Releitura é idempotente (reprocessar uma partição não duplica).

## Estado final (gabarito para o próximo capítulo)

Lake on-prem funcional: raw em HDFS, curated em Parquet, catálogo no metastore. A rigidez de escalar storage e compute juntos motiva o [cap. 09](../09-migracao-hdfs-para-s3): mover o storage para S3/MinIO.

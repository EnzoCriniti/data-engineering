# Capítulo 08 — Data Lake on-prem com HDFS 🟡

> **De onde viemos:** a plataforma já tem OLTP, warehouse, dbt, API externa e Airflow. Agora o volume de dados semi-estruturados cresce e a empresa decide aproveitar a infraestrutura on-prem existente para criar um data lake.

## Cenário de negócio

A NuvemStore passa a receber eventos de navegação em JSON: page views, cliques, sessões e interações com produtos. Carregar tudo direto num warehouse relacional fica caro e rígido — é dado de alto volume, formato variável e valor por linha baixo.

Como a empresa já possui servidores on-prem, a primeira decisão é montar um lake em **HDFS**. Isso aproveita o hardware existente e oferece *data locality* para os jobs Spark, mas também cria um acoplamento entre storage e compute — a dor que o cap. 09 vai resolver.

## O que esta etapa mostra

Um lake distribuído com três peças clássicas, todas no `docker-compose.yml`:

- **HDFS** (namenode + datanode) — o storage distribuído.
- **Spark** (master + worker) — o motor de processamento distribuído.
- **Hive Metastore** — o catálogo que registra as tabelas e os datasets do lake.

O padrão de dados é **schema-on-read**: o JSON cru entra como está e o schema é aplicado na leitura pelo Spark, não na escrita.

## Conceitos

**Data lake e schema-on-read.** Diferente do warehouse (schema-on-write, tudo tipado na entrada), o lake guarda o dado bruto e aplica estrutura só na leitura. Ganha flexibilidade para dados semi-estruturados; perde as garantias automáticas de qualidade.

**HDFS e data locality.** O HDFS distribui blocos entre datanodes; o Spark agenda a computação perto do dado, reduzindo o tráfego de rede. É a vantagem do on-prem acoplado — e também sua rigidez, porque storage e compute crescem juntos.

**Metastore como catálogo.** O Hive Metastore guarda o mapa "este caminho no lake é esta tabela, com estas colunas". Sem ele, o lake vira um amontoado de arquivos sem semântica.

**Spark como motor distribuído.** Lê JSON/CSV cru, converte para **Parquet** curado (colunar, comprimido, tipado) e registra no metastore. Conceitos de performance a dominar: shuffle, particionamento, broadcast join e skew.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe HDFS, Spark e o metastore prontos para receber jobs; a ingestão e a curadoria (`ingest_raw.py`, `build_curated.py`) são o roteiro de construção descrito no BUILD.

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o lake (HDFS + Spark + metastore) e acessar as UIs.
- **[BUILD.md](./BUILD.md)** — o roteiro de implementação dos jobs Spark: JSON cru → Parquet curado, registro no metastore e o plano de migração desde o warehouse.

## A dor que sobra

O lake em HDFS funciona, mas operar storage on-prem é rígido: storage e compute escalam juntos, a manutenção pesa e a empresa quer elasticidade. → [Capítulo 09: migração de HDFS para S3/MinIO](../09-migracao-hdfs-para-s3).

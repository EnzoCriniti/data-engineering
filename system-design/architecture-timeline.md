# Evolucao temporal da arquitetura

Esta trilha deve ser lida como uma empresa aumentando maturidade, nao como uma arquitetura que nasceu pronta.

## Fase 1 - Aplicacao e origem

Capitulos: `00`, `01`

Componentes centrais:

- backend e-commerce;
- OLTP;
- modelo dimensional desenhado.

Estado: ainda nao ha plataforma de dados real. Existe entendimento de dominio e modelagem.

## Fase 2 - Analytics inicial

Capitulos: `02`, `03`, `04`

Componentes centrais:

- analytics dentro do mesmo OLTP;
- depois warehouse dedicado;
- ELT batch com Python.

Legado criado:

- analytics no mesmo banco vira uma solucao superada;
- SQL manual vira referencia, mas depois perde protagonismo para dbt.

## Fase 3 - Transformacao e multiplas fontes

Capitulos: `05`, `06`, `07`

Componentes centrais:

- dbt;
- API externa batch;
- Airflow.

Estado: a empresa passa a ter mais de uma fonte e precisa coordenar cargas.

## Fase 4 - Lake on-prem e migracao para object storage

Capitulos: `08`, `09`

Componentes centrais:

- HDFS on-prem;
- Spark;
- metastore;
- MinIO/S3 como alvo moderno.

Legado:

- HDFS foi uma decisao inicial para aproveitar infraestrutura existente;
- depois vira legado/migracao, nao destino final.

## Fase 5 - Lakehouse

Capitulo: `10`

Componentes centrais:

- Delta Lake;
- bronze/silver/gold;
- Trino;
- Metabase.

Legado relativo:

- warehouse relacional continua util, mas deixa de ser a camada analitica principal para historico grande.

## Fase 6 - Baixa latencia

Capitulos: `11`, `12`

Componentes centrais:

- CDC com Debezium;
- Redpanda/Kafka;
- streaming com estado.

Estado: a plataforma deixa de ser apenas batch.

## Fase 7 - Dados para ML

Capitulo: `13`

Componentes centrais:

- feature table;
- features historicas e recentes;
- base para scoring de fraude.

Estado final: a plataforma atende BI, operacoes, near real-time e casos iniciais de ML.

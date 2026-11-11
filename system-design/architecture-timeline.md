# Evolucao temporal da arquitetura

Esta trilha deve ser lida como uma empresa aumentando maturidade, não como uma arquitetura que nasceu pronta.

## Fase 1 - Aplicação e origem

Capítulos: `00`, `01`

Componentes centrais:

- backend e-commerce;
- OLTP;
- modelo dimensional desenhado.

Estado: ainda não ha plataforma de dados real. Existe entendimento de domínio e modelagem.

## Fase 2 - Analytics inicial

Capítulos: `02`, `03`, `04`

Componentes centrais:

- analytics dentro do mesmo OLTP;
- depois warehouse dedicado;
- ELT batch com Python.

Legado criado:

- analytics no mesmo banco vira uma solucao superada;
- SQL manual vira referência, mas depois perde protagonismo para dbt.

## Fase 3 - Transformacao e múltiplas fontes

Capítulos: `05`, `06`, `07`

Componentes centrais:

- dbt;
- API externa batch;
- Airflow.

Estado: a empresa passa a ter mais de uma fonte e precisa coordenar cargas.

## Fase 4 - Lake on-prem e migracao para object storage

Capítulos: `08`, `09`

Componentes centrais:

- HDFS on-prem;
- Spark;
- metastore;
- MinIO/S3 como alvo moderno.

Legado:

- HDFS foi uma decisão inicial para aproveitar infraestrutura existente;
- depois vira legado/migracao, não destino final.

## Fase 5 - Lakehouse

Capítulo: `10`

Componentes centrais:

- Delta Lake;
- bronze/silver/gold;
- Trino;
- Metabase.

Legado relativo:

- warehouse relacional contínua util, mas deixa de ser a camada analítica principal para histórico grande.

## Fase 6 - Baixa latência

Capítulos: `11`, `12`

Componentes centrais:

- CDC com Debezium;
- Redpanda/Kafka;
- streaming com estado.

Estado: a plataforma deixa de ser apenas batch.

## Fase 7 - Dados para ML

Capítulo: `13`

Componentes centrais:

- feature table;
- features históricas e recentes;
- base para scoring de fraude.

Estado nesta fase: a arquitetura atende BI, Operações e Risco, com requisitos de latência diferentes.

## Fase 8 — Controles operacionais e consolidação

Capítulos 14 a 17.

À medida que os times passam a depender dos mesmos dados, a NuvemStore precisa recriar ambientes, detectar mudanças nas fontes e acompanhar a atualização das tabelas. Os capítulos finais descrevem infraestrutura como código, contratos de dados e alertas de atraso. O [capstone](../17-capstone-consolidacao) reúne o desenho final e as evidências coletadas.

# Plataforma de dados

## Fontes

| Fonte | Tipo | Latencia | Entra na trilha |
| --- | --- | --- | --- |
| PostgreSQL OLTP | banco transacional | batch e CDC | 00, 04, 11 |
| API Transportadora | API externa | batch | 06 |
| Eventos de navegacao | arquivos/eventos | batch | 08 |
| Eventos GPS | stream | tempo real | 12 |

## Camadas de dados

| Camada | Papel | Exemplo |
| --- | --- | --- |
| OLTP | sistema de escrita | `pedido`, `pagamento`, `entrega` |
| Staging | chegada bruta controlada | `staging.transportadora_entregas` |
| Warehouse | marts relacionais iniciais | `mart_receita_diaria` |
| Lake raw | dados crus em arquivo | JSON de eventos |
| Lake curated | dados tratados em Parquet | eventos normalizados |
| Bronze | dado fiel a origem | Delta bronze |
| Silver | limpo e deduplicado | Delta silver |
| Gold | consumo de negocio | receita, entrega, funil |
| Features | dados para ML | `ml.fraude_pagamento_features` |

## Processamento

| Motor | Responsabilidade |
| --- | --- |
| Python | ELT inicial e extratores batch simples. |
| dbt | transformacoes SQL testaveis e documentadas. |
| Airflow | orquestracao, retries, backfill e dependencias. |
| Spark | processamento distribuido e jobs de lake/lakehouse. |
| Debezium | CDC via WAL do Postgres. |
| Redpanda/Kafka | transporte de eventos. |
| Trino | SQL interativo e federado. |

## Consumo

| Consumidor | Fonte principal |
| --- | --- |
| Metabase | marts/gold via Postgres ou Trino |
| Analistas | warehouse, gold, Trino |
| Operacoes | dashboards e metricas streaming |
| Fraude/ML | feature table |
| Engenharia | logs, metadados, qualidade e lag |

## Nomenclatura sugerida

| Tipo | Padrao |
| --- | --- |
| Staging | `staging.<fonte>_<entidade>` |
| Raw lake | `raw/<fonte>/<entidade>/dt=YYYY-MM-DD/` |
| Curated lake | `curated/<dominio>/<entidade>/dt=YYYY-MM-DD/` |
| Bronze | `bronze.<fonte>_<entidade>` |
| Silver | `silver.<dominio>_<entidade>` |
| Gold | `gold.<metrica_ou_processo>` |
| ML | `ml.<caso>_features` |

Exemplos:

```text
staging.transportadora_entregas
bronze.oltp_pagamento
silver.pedido_item
gold.receita_diaria
ml.fraude_pagamento_features
```

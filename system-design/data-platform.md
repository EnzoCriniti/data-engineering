# Plataforma de dados

## Fontes

| Fonte | Tipo | Controle | Latência | Entra na trilha |
| --- | --- | --- | --- | --- |
| PostgreSQL OLTP | banco transacional | **interna** (controlamos o schema) | batch e CDC | 00, 04, 11 |
| API Transportadora | API externa | **externa** (não controlamos) | batch | 06 |
| Eventos de navegação | arquivos/eventos | interna | batch | 08 |
| Eventos GPS | stream | interna | tempo real | 12 |

> **Interna vs externa não é detalhe.** A origem interna (OLTP) tem schema estável que nós definimos — o [seeder](../00-modelagem-transacional/README.md) simula a aplicação que a alimenta. A **API externa** representa o dado que *não controlamos*: pode mudar o payload, paginar, ter rate limit, cair e devolver duplicatas. Essa imprevisibilidade é justamente o que motiva os capítulos de ingestão resiliente (cap 06), contratos/qualidade (cap 15) e observabilidade (cap 16). A especificação dessa API está em [`06-ingestao-api-externa/API_SPEC.md`](../06-ingestao-api-externa/API_SPEC.md).
>
> Não confundir com uma eventual **API de *serving*** (downstream) — que serviria features/scores para consumo. As fontes desta tabela são todas **upstream** (entrada da plataforma).

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
| Gold | consumo de negócio | receita, entrega, funil |
| Features | dados para ML | `ml.fraude_pagamento_features` |

## Processamento

| Motor | Responsabilidade |
| --- | --- |
| Python | ELT inicial e extratores batch simples. |
| dbt | transformacoes SQL testaveis e documentadas. |
| Airflow | orquestracao, retries, backfill e dependencias. |
| Spark | processamento distribuído e jobs de lake/lakehouse. |
| Debezium | CDC via WAL do Postgres. |
| Redpanda/Kafka | transporte de eventos. |
| Trino | SQL interativo e federado. |

## Consumo

| Consumidor | Fonte principal |
| --- | --- |
| Metabase | marts/gold via Postgres ou Trino |
| Analistas | warehouse, gold, Trino |
| Operações | dashboards e métricas streaming |
| Fraude/ML | feature table |
| Engenharia | logs, metadados, qualidade e lag |

## Nomenclatura sugerida

| Tipo | Padrão |
| --- | --- |
| Staging | `staging.<fonte>_<entidade>` |
| Raw lake | `raw/<fonte>/<entidade>/dt=YYYY-MM-DD/` |
| Curated lake | `curated/<domínio>/<entidade>/dt=YYYY-MM-DD/` |
| Bronze | `bronze.<fonte>_<entidade>` |
| Silver | `silver.<domínio>_<entidade>` |
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

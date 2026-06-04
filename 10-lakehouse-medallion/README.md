# Capítulo 10 — Lakehouse + Medallion 🟡

> **De onde viemos:** no [cap. 09](../09-migracao-hdfs-para-s3) movemos o lake para object storage barato e elástico. Mas arquivos soltos no S3 não garantem transações, schema enforcement nem time travel. O lakehouse traz a confiabilidade do warehouse sobre o storage barato do lake.

## Cenário de negócio

A NuvemStore passou a depender do lake para decisões. Um job parcial ou uma escrita concorrente pode deixar dados inconsistentes e afetar dashboards. Sem transações, "leu no meio de uma escrita" vira número errado num relatório.

O lakehouse entra para dar garantias de warehouse (ACID, schema, histórico) sobre o object storage do cap. 09, organizando o dado em camadas de qualidade crescente — a arquitetura **Medallion**.

## O que esta etapa mostra

Uma camada transacional (Delta Lake) sobre o S3/MinIO, processada por Spark e consultada por Trino, organizada em três níveis:

```text
bronze  -> dado cru, fiel à origem (ingestão sem transformar)
silver  -> tipado, deduplicado, regras técnicas aplicadas
gold    -> métricas de negócio, equivalentes aos marts anteriores
```

## Conceitos

**Lakehouse.** Une o melhor dos dois mundos: storage barato e aberto do lake + garantias transacionais do warehouse. Não é um produto, é um padrão habilitado por formatos como Delta Lake e Iceberg.

**Delta Lake e o `_delta_log`.** O Delta mantém um log de transações (`_delta_log`) ao lado dos Parquet. Esse log é o que dá ACID, schema enforcement e time travel sobre arquivos imutáveis. É distinto do metastore/catálogo: o log descreve o estado da tabela; o catálogo só diz "esta tabela existe e fica aqui".

**Medallion (bronze/silver/gold).** Camadas de refinamento progressivo. Bronze preserva fidelidade à origem; silver limpa e tipa; gold entrega métricas prontas para consumo. Cada camada é um contrato claro de qualidade.

**MERGE, schema enforcement e time travel.** `MERGE` faz upsert idempotente (chave da CDC do cap. 11). Schema enforcement rejeita escrita fora do esquema. Time travel consulta versões antigas da tabela — auditoria e rollback.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe MinIO, Spark, Airflow, Trino, metastore e Metabase. Os jobs Delta (`bronze.py`, `silver.py`, `gold.py`) e os catálogos Trino são o próximo passo de implementação.

Para subir o ambiente lakehouse e acessar as UIs, veja o **[RUNBOOK.md](./RUNBOOK.md)**.

## ⚠️ Nota de produção: PII e LGPD na camada Silver

A NuvemStore armazena **dados pessoais** (`nome`, `e-mail`, `cidade` do cliente) e **dados de localização contínua** dos entregadores (eventos de GPS do cap. 12) — categorias sensíveis sob a LGPD/GDPR.

Neste portfólio os dados são sintéticos e não há risco real, mas em produção a camada **Silver é o ponto de enforcement de privacidade** da plataforma, por uma razão arquitetural clara: o Bronze preserva fidelidade à origem (auditoria), portanto PII chega íntegro até ele. A partir do Silver, todo dado que sai para consumo precisa respeitar a finalidade e o consentimento.

As técnicas aplicadas na prática, aqui no job `silver.py`:

| Técnica | Quando usar | Exemplo neste domínio |
|---|---|---|
| **Hashing** (SHA-256 + salt) | Rastrear entidade sem expor o dado | `email_hash = sha256(salt + email)` → substitui o e-mail |
| **Mascaramento** | Dado ainda legível p/ debug, mas ofuscado | `jo**@gmail.com` |
| **Pseudonimização** | Substituir PII por token reversível (chave guardada separada) | `cliente_token` em vez de `cliente_id` direto |
| **Supressão** | Campo não tem utilidade analítica | Remover `nome` da Silver se não for necessário |

A decisão de qual técnica usar pertence ao **Data Protection Officer (DPO)** e deve estar documentada no inventário de dados (RoPA — Record of Processing Activities).

> Em resumo: o Bronze pode ter PII íntegro para auditoria. O Silver não deve.

---

## O que acontece com o DW Postgres dos capítulos 03/04?

Nos capítulos 03 e 04 o Postgres warehouse e o DuckDB eram a **fonte de verdade analítica**. A partir deste capítulo, o Lakehouse assume esse papel.

Mas o Postgres não vira lixo — ele muda de função:

```
Antes (caps 03/04):   OLTP → Postgres DW (source of truth analítica)
Depois (cap 10+):     OLTP → Lakehouse Gold (source of truth analítica)
                                 ↓ Reverse ETL
                      Postgres DW (Serving Layer para baixa latência)
```

**Por que manter o Postgres como Serving Layer?**

O Trino é excelente para queries ad hoc e exploratórias sobre petabytes. Mas tem latência de segundos a dezenas de segundos por query — inaceitável para um dashboard operacional que atualiza a cada segundo ou para uma API de produto que responde em < 100ms.

A solução padrão é o **Reverse ETL**: um job periódico lê as tabelas Gold do lakehouse e as materializa (replica) em tabelas Postgres indexadas. O Postgres entrega a query em < 10ms com um índice bem colocado; o Trino faz a análise exploratória. Ferramentas como Census, Hightouch e dbt (com `--target prod-postgres`) automatizam esse padrão.

Nesta plataforma: o Postgres continua disponível como Serving Layer para o Metabase e para qualquer integração que precise de baixa latência. O Lakehouse Gold é a fonte de verdade; o Postgres é o espelho otimizado para leitura rápida.

---

## A dor que sobra

Mesmo confiável, o lakehouse ainda é batch. Para reduzir a latência, a próxima dor é capturar mudanças continuamente, direto do banco. → [Capítulo 11: CDC com Debezium](../11-cdc-com-debezium).

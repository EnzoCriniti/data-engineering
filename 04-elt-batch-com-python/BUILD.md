# Build — Capítulo 04: como construir o ELT batch

> Guia **avançado e detalhado** de construção. Para apenas executar, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Implementar um pipeline ELT em Python que extrai o OLTP, carrega uma área raw no DuckDB e transforma em marts com SQL — explícito e idempotente, sem framework escondendo o trabalho.

## Pré-requisitos de conhecimento

- Python e psycopg2 (acesso ao Postgres).
- DuckDB e SQL analítico (agregações, JOINs).
- Diferença ELT vs ETL (ver [TECHNICAL.md](./TECHNICAL.md)).

## Estado inicial

O estado final do [cap. 03](../03-warehouse-dedicado): origem OLTP populável. Aqui trocamos a carga monolítica por um pipeline em camadas (raw → marts) sobre DuckDB.

## Passo 1 — Definir o ambiente (`docker-compose.yml`)

Serviços: `oltp` (origem, schema do cap. 00), `seeder` (profile `jobs`, reaproveitado do cap. 00) e `pipeline` (profile `jobs`). O `pipeline` monta um volume local para gravar o `.duckdb`. O `metabase` fica num passo opcional à parte.

## Passo 2 — Extração e carga do raw (`pipeline/pipeline.py`)

Para cada tabela da origem:

- `SELECT *` no Postgres, lê colunas via `cursor.description`.
- Cria `raw_<tabela>` no DuckDB tipando tudo como `VARCHAR` — o raw é fiel, sem impor tipos cedo demais; a tipagem correta acontece na transformação.
- Normaliza `Decimal → float` antes de inserir (DuckDB não recebe `Decimal` do psycopg2 diretamente).
- Carga em lote com `executemany`.

Decisão: **dropar e recriar** cada `raw_*` a cada execução (`DROP TABLE IF EXISTS`) garante idempotência da camada raw.

## Passo 3 — Construir os marts (`build_marts`)

Dois marts com `CREATE OR REPLACE TABLE`:

- `mart_receita_diaria`: receita e nº de pedidos por dia, excluindo `cancelado`. Faz `CAST` explícito dos campos que vieram como VARCHAR do raw.
- `mart_top_produtos`: top 20 por receita, com JOIN raw_item_pedido → raw_produto → raw_categoria.

`CREATE OR REPLACE` torna a etapa de transformação idempotente e reexecutável isoladamente.

## Passo 4 — Empacotar (`pipeline/Dockerfile`)

`python:3.12-slim`, instala `psycopg2-binary` e `duckdb`, roda `pipeline.py`. Vira o serviço `pipeline`.

## Validações (definição de pronto)

- [ ] `pipeline` roda do zero sem erro e gera o `.duckdb`.
- [ ] Todas as `raw_*` têm contagem = contagem na origem.
- [ ] Receita total em `mart_receita_diaria` = receita de itens não cancelados no OLTP.
- [ ] Rodar o pipeline duas vezes seguidas não muda os marts (idempotência).
- [ ] `python -m py_compile pipeline/pipeline.py` passa.

## Estado final (gabarito para o próximo capítulo)

DuckDB com camada raw fiel à origem e dois marts validados por reconciliação. As transformações, porém, são SQL solto em Python — sem testes nem lineage. Gancho para o [dbt no cap. 05](../05-transformacao-com-dbt), que reaproveita esses marts como referência de equivalência.

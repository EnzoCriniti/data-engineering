# Solução — Cap. 05: Transformação com dbt

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
05-transformacao-com-dbt/
├── .env.example
├── docker-compose.yml
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── schema.yml
│   │   ├── stg_clientes.sql
│   │   ├── stg_produtos.sql
│   │   ├── stg_pedidos.sql
│   │   ├── stg_itens_pedido.sql
│   │   └── stg_pagamentos.sql
│   └── marts/
│       ├── mart_receita_diaria.sql
│       └── mart_top_produtos.sql
└── diagrams/
    └── architecture.py
```

## `docker-compose.yml`

O capítulo é de transformação (dbt roda como CLI), então o compose entrega só a **camada de BI** (Metabase) que consome os marts. O `dbt` em si roda num serviço em perfil `jobs`, montando o `.duckdb` gerado no cap 04.

```yaml
services:
  # Camada de BI — consome os marts materializados no DuckDB
  metabase:
    image: metabase/metabase:latest
    container_name: p05-metabase
    ports:
      - "${METABASE_PORT:-3002}:3000"
    volumes:
      - metabase-data:/metabase-data
    environment:
      MB_DB_FILE: /metabase-data/metabase.db

  # Runner dbt — só sobe quando chamado explicitamente (perfil jobs)
  dbt:
    image: ghcr.io/dbt-labs/dbt-duckdb:1.7.latest
    container_name: p05-dbt
    working_dir: /usr/app
    volumes:
      - ./:/usr/app                 # projeto dbt (dbt_project.yml, models/)
      - ./profiles.yml:/root/.dbt/profiles.yml:ro
      - ../04-elt-batch-com-python/data/warehouse:/usr/app/data/warehouse
    environment:
      DUCKDB_PATH: /usr/app/data/warehouse/nuvemstore.duckdb
    entrypoint: ["dbt"]
    command: ["build"]
    profiles: [jobs]

volumes:
  metabase-data:
```

> Os comandos `dbt build` / `dbt docs` do RUNBOOK podem rodar localmente (com `dbt-duckdb` instalado) **ou** via `docker compose --profile jobs run --rm dbt build`. O `.duckdb` vem do capítulo 04 — por isso o volume aponta para `../04-elt-batch-com-python/data/warehouse`.

## `dbt_project.yml`

```yaml
name: nuvemstore
version: '1.0.0'
profile: nuvemstore

model-paths: ["models"]
target-path: "target"
clean-targets: ["target", "dbt_packages"]

models:
  nuvemstore:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

## `profiles.yml`

```yaml
nuvemstore:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DUCKDB_PATH', 'data/warehouse/nuvemstore.duckdb') }}"
      threads: 4
```

## `models/staging/schema.yml`

```yaml
version: 2

sources:
  - name: raw
    tables:
      - name: raw_cliente
      - name: raw_produto
      - name: raw_categoria
      - name: raw_pedido
      - name: raw_item_pedido
      - name: raw_pagamento

models:
  - name: stg_clientes
    columns:
      - name: cliente_id
        tests: [not_null, unique]
  - name: stg_produtos
    columns:
      - name: produto_id
        tests: [not_null, unique]
  - name: stg_pedidos
    columns:
      - name: pedido_id
        tests: [not_null, unique]
  - name: stg_itens_pedido
    columns:
      - name: item_pedido_id
        tests: [not_null, unique]
```

## `models/staging/stg_clientes.sql`

```sql
SELECT
    CAST(cliente_id AS INTEGER)  AS cliente_id,
    CAST(nome       AS VARCHAR)  AS nome,
    CAST(cidade     AS VARCHAR)  AS cidade,
    CAST(email      AS VARCHAR)  AS email
FROM {{ source('raw', 'raw_cliente') }}
```

## `models/staging/stg_produtos.sql`

```sql
SELECT
    CAST(p.produto_id   AS INTEGER) AS produto_id,
    CAST(p.nome         AS VARCHAR) AS nome,
    CAST(c.nome         AS VARCHAR) AS categoria,
    CAST(p.preco        AS DOUBLE)  AS preco
FROM {{ source('raw', 'raw_produto') }}   p
JOIN {{ source('raw', 'raw_categoria') }} c
  ON c.categoria_id = p.categoria_id
```

## `models/staging/stg_pedidos.sql`

```sql
SELECT
    CAST(pedido_id   AS INTEGER)   AS pedido_id,
    CAST(cliente_id  AS INTEGER)   AS cliente_id,
    CAST(data_pedido AS TIMESTAMP) AS data_pedido,
    CAST(status      AS VARCHAR)   AS status
FROM {{ source('raw', 'raw_pedido') }}
```

## `models/staging/stg_itens_pedido.sql`

```sql
SELECT
    CAST(item_pedido_id AS INTEGER) AS item_pedido_id,
    CAST(pedido_id      AS INTEGER) AS pedido_id,
    CAST(produto_id     AS INTEGER) AS produto_id,
    CAST(quantidade     AS INTEGER) AS quantidade,
    CAST(preco_unitario AS DOUBLE)  AS preco_unitario
FROM {{ source('raw', 'raw_item_pedido') }}
```

## `mo
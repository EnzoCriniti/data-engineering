# Capitulo 04 - ELT batch com Python

> De onde viemos: do modelo transacional do capitulo 00. Agora a origem OLTP existe de verdade e precisa ser extraida sem pesar no banco de producao.

## Cenario de negocio

A NuvemStore e um e-commerce pequeno. Pedidos, clientes e produtos vivem num PostgreSQL transacional que atende o site. O time de negocio quer relatorios de receita diaria e top produtos, mas rodar consultas analiticas direto no OLTP degrada o checkout.

A solucao deste capitulo e simples de proposito: extrair os dados do Postgres, carregar uma area raw no DuckDB e transformar com SQL escrito a mao.

## Por que esta stack

| Tecnologia | Por que |
| --- | --- |
| PostgreSQL | Origem transacional normalizada, reaproveitada do capitulo 00. |
| Python + psycopg2 | Extracao explicita, sem framework escondendo o trabalho. |
| DuckDB | Warehouse analitico local, leve e facil de inspecionar. |
| SQL escrito a mao | Mostra a dor que o dbt resolve no capitulo 05. |
| Docker Compose | Sobe cada parte do ambiente em etapas visiveis. |

## Arquitetura

![Arquitetura](./diagrams/architecture.png)

Codigo do diagrama: [`diagrams/architecture.py`](./diagrams/architecture.py).

## Como rodar por etapas

Copie o arquivo de ambiente:

```bash
cp .env.example .env
```

Suba apenas a origem OLTP:

```bash
docker compose up -d oltp
```

Popule a origem com dados sinteticos:

```bash
docker compose run --rm seeder
```

Execute o ELT batch com Python:

```bash
docker compose run --rm pipeline
```

O pipeline cria o DuckDB em:

```text
04-elt-batch-com-python/data/warehouse/nuvemstore.duckdb
```

Para refazer a demonstracao do zero, removendo volumes e dados locais do compose:

```bash
docker compose down -v
docker compose up -d oltp
docker compose run --rm seeder
docker compose run --rm pipeline
```

## Saidas geradas

O pipeline cria tabelas raw para cada tabela da origem:

```text
raw_cliente
raw_categoria
raw_produto
raw_pedido
raw_item_pedido
raw_pagamento
raw_entregador
raw_entrega
```

E dois marts simples:

```text
mart_receita_diaria
mart_top_produtos
```

## Camada de BI

O Metabase fica separado do fluxo principal para nao esconder as etapas do pipeline:

```bash
docker compose up -d metabase
```

UI:

```text
http://localhost:3001
```

Nota tecnica: neste capitulo o warehouse e DuckDB. Para conectar o Metabase diretamente nele, use o driver community de DuckDB; no capitulo 05 a saida analitica passa a ser materializada em Postgres para facilitar a conexao nativa do BI.

## A dor que sobra

O pipeline funciona, mas o SQL esta solto, sem testes, sem lineage e sem contratos de dados. Essa fragilidade e exatamente a motivacao do capitulo 05: transformacao com dbt.

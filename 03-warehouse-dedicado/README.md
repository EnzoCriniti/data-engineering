# Capitulo 03 - Warehouse dedicado

> De onde viemos: no capitulo 02, o dimensional ficou em outro schema, mas ainda dentro do mesmo Postgres da aplicacao. A separacao era logica, nao operacional.

## Cenario de negocio

As consultas analiticas da NuvemStore cresceram. Relatorios de receita, produto e cliente comecaram a competir com o checkout e com as escritas transacionais.

A resposta agora e separar fisicamente as bases:

```text
oltp       -> Postgres da aplicacao
warehouse  -> Postgres dedicado para analytics
```

## O que esta etapa entrega

Esta etapa sobe dois bancos no Docker:

- `oltp`: origem transacional, com o schema do capitulo 00.
- `warehouse`: base analitica dedicada, com schema dimensional.
- `seeder`: job opcional para popular a origem.
- `migrate`: job opcional para materializar dimensoes e fato no warehouse.

Mesmo usando Postgres nos dois lados, a arquitetura muda: agora analytics nao compete com o banco da aplicacao.

## Como rodar o ambiente base

```bash
cp .env.example .env
docker compose up -d oltp warehouse
```

## Como popular e migrar dados

```bash
docker compose run --rm seeder
docker compose run --rm migrate
```

Para refazer do zero:

```bash
docker compose down -v
docker compose up -d oltp warehouse
docker compose run --rm seeder
docker compose run --rm migrate
```

## A dor que sobra

Agora existe isolamento fisico, mas a carga e a transformacao ainda sao simples demais. Conforme o SQL cresce, faltam testes, lineage e modularidade. Essa dor leva ao capitulo 04 e depois ao dbt no capitulo 05.

# Runbook — Capítulo 02: dimensional no mesmo OLTP

> Guia rápido para **subir e usar**. Este capítulo materializa o star schema do cap. 01 dentro do mesmo Postgres, num schema `analytics` ao lado do `public` (OLTP).

## O que este capítulo entrega

Um único Postgres com dois schemas: `public` (tabelas OLTP do cap. 00) e `analytics` (tabelas dimensionais `dim_tempo`, `dim_cliente`, `dim_produto`, `fct_vendas`). A origem é populada com dados sintéticos; as tabelas dimensionais sobem criadas e vazias — o foco aqui é mostrar a convivência dos dois mundos no mesmo motor.

## Pré-requisitos

- Docker e Docker Compose.
- Porta `5434` livre (configurável no `.env`).

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d db
docker compose run --rm seeder
```

O Postgres sobe já com os dois schemas: o `public` vem do `schema.sql` do cap. 00 e o `analytics` do `ddl/analytics.sql` deste capítulo (ambos montados como scripts de inicialização). O seeder popula a origem.

Saída esperada do seeder:

```text
Seed concluido: 250 clientes, 1200 pedidos.
```

## Conferir

Verifique que os dois schemas coexistem no mesmo banco:

```bash
docker compose exec db psql -U app -d nuvemstore -c "\dn"
docker compose exec db psql -U app -d nuvemstore -c "\dt analytics.*"
docker compose exec db psql -U app -d nuvemstore -c "SELECT count(*) FROM public.pedido;"
```

Você verá os schemas `public` e `analytics`, as quatro tabelas dimensionais (vazias) e a contagem de pedidos da origem populada.

## Ajustes comuns

| Variável | Default | Efeito |
|---|---|---|
| `DB_PORT` | `5434` | Porta exposta no host |
| `SEED_CUSTOMERS` | `250` | Clientes gerados |
| `SEED_ORDERS` | `1200` | Pedidos gerados |
| `SEED_RESET` | `true` | Limpa antes de popular (idempotência) |

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d db
docker compose run --rm seeder
```

## Próximo passo

[Capítulo 03](../03-warehouse-dedicado): separar fisicamente origem e warehouse em dois Postgres, com um job `migrate` que carrega o dimensional resolvendo as surrogate keys.

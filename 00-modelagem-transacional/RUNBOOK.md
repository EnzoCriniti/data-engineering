# Runbook — Capítulo 00: origem transacional (OLTP)

> Guia rápido para **subir e usar** o ambiente. Nada aqui precisa ser construído do zero: o schema e o seeder já estão prontos no repositório. Você só executa comandos e observa o resultado.

## O que este capítulo entrega

Uma origem transacional reproduzível da NuvemStore: um PostgreSQL com o schema OLTP normalizado (oito tabelas) e um seeder que popula dados sintéticos coerentes (clientes, produtos, pedidos, pagamentos e entregas).

O capítulo 00 não tem um `docker-compose.yml` próprio — ele é a **fundação compartilhada**. O schema (`ddl/schema.sql`) e o seeder (`seed/`) são reaproveitados por todos os capítulos seguintes. A primeira vez que a origem realmente sobe é no capítulo 02.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Porta `5434` livre (ou ajuste `DB_PORT` no `.env`).

## Subir a origem (via capítulo 02)

```bash
cd ../02-dimensional-no-oltp
cp .env.example .env
docker compose up -d db
```

O Postgres sobe e o `schema.sql` deste capítulo é aplicado automaticamente na inicialização (montado em `/docker-entrypoint-initdb.d`). **Você não roda o DDL na mão.**

## Popular com dados sintéticos

```bash
docker compose run --rm seeder
```

Saída esperada:

```text
Seed concluido: 250 clientes, 1200 pedidos.
```

O seeder é **idempotente**: rodar de novo com `SEED_RESET=true` (padrão) limpa as tabelas e recria os dados com a mesma seed (42), então o resultado é sempre o mesmo.

## Conferir que a origem está populada

```bash
docker compose exec db psql -U app -d nuvemstore -c "
  SELECT 'cliente' AS tabela, COUNT(*) FROM cliente
  UNION ALL SELECT 'pedido', COUNT(*) FROM pedido
  UNION ALL SELECT 'item_pedido', COUNT(*) FROM item_pedido
  UNION ALL SELECT 'pagamento', COUNT(*) FROM pagamento
  UNION ALL SELECT 'entrega', COUNT(*) FROM entrega;"
```

Você deve ver contagens > 0 em todas as tabelas. Uma consulta de negócio rápida para ver o dado "vivo":

```bash
docker compose exec db psql -U app -d nuvemstore -c "
  SELECT c.nome AS categoria, SUM(i.quantidade * i.preco_unitario) AS receita
  FROM item_pedido i
  JOIN produto p ON p.id = i.produto_id
  JOIN categoria c ON c.id = p.categoria_id
  GROUP BY 1 ORDER BY 2 DESC;"
```

Repare: já para uma pergunta simples ("receita por categoria") foram necessárias três junções. Essa é exatamente a dor que motiva a modelagem dimensional do capítulo 01.

## Ajustes comuns

| Variável | Padrão | Para quê |
| --- | --- | --- |
| `SEED_CUSTOMERS` | 250 | Quantidade de clientes gerados. |
| `SEED_ORDERS` | 1200 | Quantidade de pedidos gerados. |
| `SEED_RESET` | true | Limpa antes de popular (idempotência). |
| `DB_PORT` | 5434 | Porta exposta no host. |

## Recomeçar do zero

```bash
docker compose down -v   # apaga o volume e os dados
docker compose up -d db
docker compose run --rm seeder
```

## Próximo passo

Com a origem populada, siga para o [capítulo 01](../01-modelagem-dimensional) (modelo dimensional) e depois o [capítulo 02](../02-dimensional-no-oltp), que coloca analytics no mesmo banco para sentir o limite dessa abordagem.

# Runbook — Capítulo 03: warehouse dedicado

> Guia rápido para **subir e usar** o ambiente. Tudo já está pronto no repositório — você executa comandos e observa o resultado. Nada para construir aqui.

## O que este capítulo entrega

Dois bancos PostgreSQL fisicamente separados e um job que materializa o modelo dimensional:

```text
oltp       -> Postgres da aplicação (schema do cap 00)
warehouse  -> Postgres dedicado a analytics (schema dimensional)
```

A separação física faz analytics parar de competir com o checkout. O job `migrate` lê do `oltp` e carrega dimensões e fato no `warehouse`.

## Pré-requisitos

- Docker e Docker Compose.
- Portas `5435` (oltp) e `5436` (warehouse) livres, ou ajuste no `.env`.

## Passo 1 — Subir os dois bancos

```bash
cp .env.example .env
docker compose up -d oltp warehouse
```

Os schemas são aplicados automaticamente na inicialização: o `oltp` recebe o `schema.sql` do cap 00, o `warehouse` recebe o `warehouse/schema.sql` (modelo dimensional). Aguarde os healthchecks ficarem saudáveis:

```bash
docker compose ps
```

## Passo 2 — Popular a origem

```bash
docker compose run --rm seeder
```

Saída esperada: `Seed concluido: 250 clientes, 1200 pedidos.`

## Passo 3 — Migrar para o warehouse

```bash
docker compose run --rm migrate
```

Saída esperada (números podem variar conforme a seed):

```text
Migracao concluida: 250 clientes, 56 produtos, ~2600 itens vendidos.
```

O que aconteceu: o job truncou as tabelas analíticas, carregou `dim_cliente`, `dim_produto` e `dim_tempo`, e então populou `fct_vendas` resolvendo cada chave natural para a surrogate key correspondente.

## Passo 4 — Conferir o resultado no warehouse

```bash
docker compose exec warehouse psql -U analytics -d warehouse -c "
  SELECT dp.categoria, SUM(f.valor_total) AS receita
  FROM analytics.fct_vendas f
  JOIN analytics.dim_produto dp ON dp.sk_produto = f.sk_produto
  GROUP BY 1 ORDER BY 2 DESC;"
```

A mesma pergunta do cap 00 ("receita por categoria") agora roda no banco analítico, sem tocar o transacional e sobre um modelo desenhado para leitura.

### Validação de equivalência

Compare a receita total nas duas pontas — devem bater:

```bash
# origem (OLTP)
docker compose exec oltp psql -U app -d nuvemstore -t -c "
  SELECT ROUND(SUM(i.quantidade*i.preco_unitario),2)
  FROM item_pedido i JOIN pedido p ON p.id=i.pedido_id
  WHERE p.status <> 'cancelado';"
# destino (warehouse)
docker compose exec warehouse psql -U analytics -d warehouse -t -c "
  SELECT ROUND(SUM(valor_total),2) FROM analytics.fct_vendas;"
```

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d oltp warehouse
docker compose run --rm seeder
docker compose run --rm migrate
```

## Próximo passo

A carga aqui é um script só. Conforme o SQL cresce, faltam testes, modularidade e lineage — a dor que leva ao [capítulo 04](../04-elt-batch-com-python) (ELT batch) e depois ao dbt no [capítulo 05](../05-transformacao-com-dbt).

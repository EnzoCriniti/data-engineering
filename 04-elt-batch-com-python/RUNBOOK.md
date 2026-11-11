# Runbook — Capítulo 04: ELT batch com Python

> Guia rápido para **subir e usar** o pipeline já pronto. Você executa comandos e observa o resultado; nada para construir aqui.

## O que este capítulo entrega

Um pipeline ELT que extrai o OLTP, carrega tabelas `raw_*` num DuckDB e materializa dois marts (`mart_receita_diaria`, `mart_top_produtos`).

## Pré-requisitos

- Docker e Docker Compose.
- Porta `5435` livre ou outro valor para `OLTP_PORT` no `.env`.
- Execute os comandos da pasta `04-elt-batch-com-python`. Os exemplos usam um shell Bash.

## Passo 1 — Preparar ambiente e subir a origem

```bash
cp .env.example .env
docker compose up -d --wait oltp
```

O comando aguarda o Postgres passar no healthcheck.

## Passo 2 — Popular a origem

```bash
docker compose run --rm seeder
```

Com os valores padrão, o seeder informa `Seed concluído: 250 clientes, 1200 pedidos.`

## Passo 3 — Rodar o ELT batch

```bash
docker compose run --rm pipeline
```

Saída esperada (uma linha por tabela raw + os marts):

```text
raw_cliente: 250 linhas
raw_pedido: 1200 linhas
...
mart_receita_diaria criado.
mart_top_produtos criado.
Pipeline concluído.
```

O arquivo DuckDB aparece em `data/warehouse/nuvemstore.duckdb`.

## Passo 4 — Conferir os marts

Use a própria imagem do pipeline para consultar o DuckDB:

```bash
docker compose run --rm --no-deps pipeline python -c \
  'import duckdb, os; db = duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True); db.sql("SELECT * FROM mart_top_produtos ORDER BY receita DESC LIMIT 5").show()'
```

Compare a contagem de pedidos e a receita dos itens de pedidos não cancelados entre o Postgres e o DuckDB:

```bash
docker compose exec -T oltp psql -U nuvemstore -d nuvemstore -c \
  "SELECT COUNT(DISTINCT p.pedido_id) AS pedidos, ROUND(SUM(i.quantidade * i.preco_unitario), 2) AS receita
   FROM pedido p JOIN item_pedido i USING (pedido_id) WHERE p.status <> 'cancelado';"
docker compose run --rm --no-deps pipeline python -c \
  'import duckdb, os; db = duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True); db.sql("SELECT SUM(total_pedidos) AS pedidos, ROUND(SUM(receita), 2) AS receita FROM mart_receita_diaria").show()'
```

As duas consultas devem retornar a mesma contagem e receita.

## Repetir a verificação do CI

Com a origem populada e o primeiro lote executado, rode:

```bash
docker compose run --rm --no-deps -T pipeline python - < pipeline/verify.py
docker compose run --rm --no-deps -T pipeline
docker compose run --rm --no-deps -T pipeline python - < pipeline/verify.py
```

O verificador compara as oito tabelas raw, a contagem de pedidos e a receita de cada dia com o PostgreSQL. Ele também confirma que o ranking tem 20 produtos para os dados de demonstração. As duas verificações devem terminar com `Reconciliação OK`. Para encerrar e preservar os dados, rode `docker compose down`.

## Recomeçar do zero

Os comandos abaixo apagam os dados de demonstração deste capítulo.

```bash
docker compose down -v
rm -f data/warehouse/nuvemstore.duckdb
docker compose up -d --wait oltp
docker compose run --rm seeder
docker compose run --rm pipeline
```

## Próximo passo

[Capítulo 05](../05-transformacao-com-dbt): reescrever essas transformações como modelos dbt testáveis.

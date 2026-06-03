# Runbook — Capítulo 04: ELT batch com Python

> Guia rápido para **subir e usar** o pipeline já pronto. Você executa comandos e observa o resultado; nada para construir aqui.

## O que este capítulo entrega

Um pipeline ELT que extrai o OLTP, carrega tabelas `raw_*` num DuckDB e materializa dois marts (`mart_receita_diaria`, `mart_top_produtos`).

## Pré-requisitos

- Docker e Docker Compose.
- Porta da origem livre (ver `.env`). Para o BI, porta `3001`.

## Passo 1 — Preparar ambiente e subir a origem

```bash
cp .env.example .env
docker compose up -d oltp
```

Aguarde o healthcheck: `docker compose ps`.

## Passo 2 — Popular a origem

```bash
docker compose run --rm seeder
```

Saída esperada: `Seed concluido: 250 clientes, 1200 pedidos.`

## Passo 3 — Rodar o ELT batch

```bash
docker compose run --rm pipeline
```

Saída esperada (uma linha por tabela raw + os marts):

```text
raw_cliente: 250 linhas
raw_pedido: 1200 linhas
...
marts: mart_receita_diaria, mart_top_produtos
Pipeline concluido: /warehouse/nuvemstore.duckdb
```

O arquivo DuckDB aparece em `data/warehouse/nuvemstore.duckdb`.

## Passo 4 — Conferir os marts

Se tiver o CLI do DuckDB localmente:

```bash
duckdb data/warehouse/nuvemstore.duckdb \
  "SELECT * FROM mart_top_produtos LIMIT 5;"
```

Ou inspecione via Python:

```bash
python -c "import duckdb; print(duckdb.connect('data/warehouse/nuvemstore.duckdb').sql('SELECT SUM(receita) FROM mart_receita_diaria'))"
```

**Validação de equivalência:** a soma de `receita` em `mart_receita_diaria` deve bater com a receita de itens não cancelados na origem.

## Passo 5 (opcional) — BI

```bash
docker compose up -d metabase
# UI: http://localhost:3001
```

> Neste capítulo o warehouse é DuckDB; use o driver community de DuckDB no Metabase. A partir do cap. 05 a saída é materializada em Postgres.

## Recomeçar do zero

```bash
docker compose down -v
rm -f data/warehouse/nuvemstore.duckdb
docker compose up -d oltp
docker compose run --rm seeder
docker compose run --rm pipeline
```

## Próximo passo

[Capítulo 05](../05-transformacao-com-dbt): reescrever essas transformações como modelos dbt testáveis.

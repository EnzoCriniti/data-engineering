# Runbook — Capítulo 05

## O que este capítulo entrega

Marts dbt de receita diária e top produtos sobre as tabelas `raw_*` do capítulo 04. O perfil grava em `analytics_dbt` e permite comparar as duas implementações no mesmo DuckDB.

## Pré-requisitos

Docker com Compose v2.20 ou posterior. Execute os comandos a partir deste capítulo, em um projeto de estudo.

## Subir e usar

```sh
docker compose --env-file .env.example up -d --wait oltp
docker compose --env-file .env.example run --rm --build seeder
docker compose --env-file .env.example run --rm --build pipeline
docker compose --env-file .env.example run --rm --build dbt
```

## Validar

O job `dbt` seleciona os dois marts de vendas e seus modelos e testes upstream. Consulte `main.mart_receita_diaria` e `analytics_dbt.mart_receita_diaria` no arquivo `../04-elt-batch-com-python/data/warehouse/nuvemstore.duckdb`. Confira contagem e receita por dia com duas casas decimais. O ranking dbt desempata por produto e categoria.

Para executar sem Docker, instale `requirements.txt`, aponte `DUCKDB_PATH` ao arquivo existente e rode `dbt build --profiles-dir . --select +mart_receita_diaria +mart_top_produtos`.

## Recomeçar do zero

Em um ambiente descartável, `docker compose --env-file .env.example down --volumes` remove o OLTP de estudo. O arquivo DuckDB fica no diretório do capítulo 04. Para repetir com estado limpo, guarde esse arquivo e use um caminho novo.

## Próximo passo

O [capítulo 06](../06-ingestao-api-externa/RUNBOOK.md) acrescenta o SLA sobre a API de exemplo.

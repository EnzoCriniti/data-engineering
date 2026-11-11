# Runbook — Capítulo 06

## O que este capítulo entrega

API mock paginada, staging incremental no DuckDB e consulta dbt para o SLA de entregas terceirizadas.

## Pré-requisitos

Docker com Compose v2.20 ou posterior. Use um projeto de estudo. Os comandos desta seção partem da pasta do capítulo.

## Subir e usar

```sh
docker compose --env-file .env.example up -d --wait oltp transportadora
docker compose --env-file .env.example run --rm --build seeder
docker compose --env-file .env.example run --rm --build pipeline
curl -H 'X-API-Key: estudo-transportadora' 'http://localhost:8088/entregas?limit=1'
docker compose --env-file .env.example run --rm --build extractor
docker compose --env-file .env.example run --rm extractor
docker compose --env-file .env.example run --rm --build dbt build --as-of 2026-06-08T16:00:00Z
docker compose --env-file .env.example run --rm dbt report
```

## Validar

A resposta HTTP tem `next_cursor` na primeira página. A primeira carga grava duas entregas de exemplo. A segunda deve gravar zero. O relatório lista o `pedido_id` associado e os segundos de atraso das entregas abertas. A fixture HTTP simples ilustra a paginação. A prova completa abaixo gera os IDs dos cenários a partir do OLTP quando recebe `OLTP_URL`.

Na raiz do repositório, em um ambiente Python isolado:

```sh
pip install -r 05-transformacao-com-dbt/requirements.txt -r 04-elt-batch-com-python/pipeline/requirements.txt
python shared/entregas/test_phase2.py
```

Sem `OLTP_URL`, a prova prepara tabelas raw descartáveis no DuckDB. Com `OLTP_URL` apontando para um **PostgreSQL descartável, com o DDL do capítulo 00 e sem dados**, ela carrega pedidos reais pelo ELT do capítulo 04. O CI executa essa segunda opção. A prova espera 1 atraso aberto, 1 entrega concluída em atraso, 2 dentro do prazo, 2 exceções terminais, 1 órfã, 1 cancelada e 1 prazo inválido. Ela interrompe a segunda página, compara dados e checkpoint e encerra com zero atrasos abertos após a correção.

## Recomeçar do zero

Em um ambiente de estudo, derrube os containers com `docker compose --env-file .env.example down --volumes`. Para refazer a prova automatizada, execute o script novamente. Ele cria um DuckDB temporário em cada execução.

## Próximo passo

O [capítulo 07](../07-orquestracao-com-airflow/RUNBOOK.md) usa os mesmos jobs em um DAG com retry e backfill.

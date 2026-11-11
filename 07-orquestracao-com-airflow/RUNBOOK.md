# Runbook — Capítulo 07

## O que este capítulo entrega

Um DAG Airflow com LocalExecutor e Postgres de metadados. Ele executa simulação, carga OLTP, carga API, `dbt build` e consulta de SLA em sequência. A carga compartilha o lock do DuckDB com os jobs manuais.

## Pré-requisitos

Docker com Compose v2.20 ou posterior. Os comandos partem da pasta do capítulo e usam credenciais de estudo. O Compose inclui o ambiente cumulativo com volumes próprios do projeto.

## Subir e usar

```sh
docker compose --env-file .env.example up -d --build --wait oltp warehouse
docker compose --env-file .env.example run --rm --build seeder
docker compose --env-file .env.example up -d --build --wait airflow-scheduler
docker compose --env-file .env.example exec airflow-scheduler airflow dags list
docker compose --env-file .env.example run --rm airflow-ativar
docker compose --env-file .env.example exec airflow-scheduler airflow dags trigger nuvemstore_daily
docker compose --env-file .env.example exec airflow-scheduler airflow dags list-runs -d nuvemstore_daily
```

O DAG é criado pausado. Ative depois de popular o OLTP. O agendamento é às 06:00 UTC. Para rodar manualmente sem gerar um lote de pedidos, use `airflow dags trigger nuvemstore_daily --conf '{"somente_reprocessar":true}'`.

## Validar e recuperar

Confira a execução `success` em `airflow dags list-runs -d nuvemstore_daily`. O job abaixo mostra contagens por situação e as entregas em atraso aberto.

```sh
docker compose --env-file .env.example run --rm --build sla
```

Se a API falhar, a tarefa `carga_api` pode retentar duas vezes depois das tentativas HTTP. Os logs ficam no volume `airflow-logs`. A transformação só inicia após a carga bem-sucedida. Para reparar um intervalo já encerrado, escolha os limites a partir das 06:00 UTC. Este exemplo seleciona o intervalo `[2026-06-08 06:00, 2026-06-09 06:00)`.

```sh
docker compose --env-file .env.example exec airflow-scheduler airflow dags backfill \
  nuvemstore_daily --start-date 2026-06-08T06:00:00Z --end-date 2026-06-08T06:00:00Z --yes
```

O backfill carrega as versões que a API ainda expõe e recompõe o mart corrente. Ele não cria pedidos históricos. Para demonstrar retry e equivalência entre CLI e DAG, rode `bash shared/entregas/airflow-e2e.sh` da raiz em um ambiente Docker descartável. O teste cria um projeto separado, interrompe a API, observa `up_for_retry`, recupera a tarefa e compara o estado depois do backfill.

## Recomeçar do zero

Use `docker compose --env-file .env.example down --volumes` somente no projeto descartável de estudo. No NAS, o redeploy deve preservar os volumes.

## Próximo passo

O [diário da fase](../docs/diario/fase-2-entregas.md) registra evidências e os passos do aceite no Agent Platform.

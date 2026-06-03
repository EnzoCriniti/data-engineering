# Build — Capítulo 07: como construir a orquestração com Airflow

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Transformar os comandos manuais dos capítulos anteriores num DAG do Airflow, com dependências explícitas, retries e backfill — sem reimplementar a lógica dos jobs.

## Pré-requisitos de conhecimento

- Conceito de DAG, operators, dependências, `data_interval`.
- Os jobs idempotentes dos caps. 00, 04, 05, 06.

## Estado inicial

Estado final do [cap. 06](../06-ingestao-api-externa): jobs de carga (OLTP, API externa) e transformações dbt existem, mas são disparados à mão.

## Passo 1 — Ambiente (`docker-compose.yml`)

Airflow `standalone` (scheduler + webserver + metadata num container), com `airflow/dags/` montado. Metabase num profile `bi` opcional.

## Passo 2 — Modelar o DAG (`airflow/dags/pipeline_nuvemstore.py`)

Tarefas e dependências:

```text
seed_oltp ─┐
           ├─> dbt_build ─> validar_marts
extrair_api┘
```

- `seed_oltp` e `extrair_api` rodam em paralelo (cargas independentes);
- `dbt_build` só roda quando ambas terminam;
- `validar_marts` confere equivalência ao final.

Use operators que **chamam os jobs existentes** (DockerOperator/BashOperator chamando `docker compose run`, ou PythonOperator importando a lógica). Não reescreva a transformação no DAG.

## Passo 3 — Parametrizar por data

Usar `{{ data_interval_start }}` para passar a janela às tasks, permitindo backfill de uma data específica. Depende da idempotência já garantida nos jobs.

## Passo 4 — Políticas operacionais

- `retries` + `retry_delay` (exponencial) nas tasks de rede (API externa);
- `sla` simples por task;
- logs por task (nativo do Airflow);
- `catchup` controlado para não disparar backfill acidental.

## Validações (definição de pronto)

- [ ] `airflow dags list` mostra o DAG sem erro de import.
- [ ] Um run completo produz os mesmos marts que a execução manual.
- [ ] Backfill de um intervalo é idempotente.
- [ ] Falha simulada na API dispara retry conforme a política.

## Estado final (gabarito para o próximo capítulo)

Pipeline como operação: agendado, ordenado, com retries e backfill. A próxima dor é escala e dados semi-estruturados — gancho para o [Data Lake com Spark no cap. 08](../08-data-lake-com-spark).

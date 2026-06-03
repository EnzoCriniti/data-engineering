# Capitulo 07 - Orquestracao com Airflow

> De onde viemos: dbt organiza transformacoes, mas nao coordena varias fontes, retries, backfill e dependencias entre pipelines.

## Cenario de negocio

A NuvemStore passa a ter multiplas fontes: Postgres de pedidos, arquivos de logistica e API de marketing. A transformacao so pode rodar depois que todas as cargas terminarem.

Cron nao sabe expressar essa dependencia de forma segura. Airflow entra para orquestrar.

## Status desta etapa

Status atual: **ambiente/documentacao**.

O compose sobe o Airflow em modo `standalone` para estudo e futura implementacao de DAGs. Os DAGs reais ainda serao adicionados depois.

## Como esta etapa migra a anterior

Airflow nao substitui dbt nem o pipeline; ele passa a coordenar o que ja existe.

Plano de migracao:

1. pegar os comandos manuais dos capitulos anteriores como tarefas do DAG;
2. transformar `seeder`, extracao/carga, dbt run e dbt test em tasks com dependencias claras;
3. parametrizar execucoes por data para permitir backfill;
4. comparar uma execucao manual com uma execucao orquestrada;
5. reduzir o uso de scripts soltos e cron depois que o DAG estiver confiavel.

## Como subir o ambiente base

```bash
cp .env.example .env
docker compose up -d airflow
```

UI do Airflow:

```text
http://localhost:8080
```

Para subir o BI opcional:

```bash
docker compose --profile bi up -d metabase
```

## O que entra na integracao futura

- DAG de ingestao de multiplas fontes.
- Task chamando o pipeline/dbt.
- Retries e backfill.
- Logs e checkpoints por data de execucao.

## A dor que sobra

Com orquestracao resolvida, a proxima dor e escala: dados semi-estruturados e volume alto. Isso leva ao capitulo 08: Data Lake com Spark.

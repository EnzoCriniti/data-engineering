# Capítulo 07 — Orquestração com Airflow

> **De onde viemos:** o dbt organiza transformações e o cap. 06 trouxe uma fonte externa, mas nada coordena as várias cargas, retries, backfill e dependências entre pipelines. Rodar tudo na mão, na ordem certa, virou frágil.

## Cenário de negócio

A NuvemStore agora tem múltiplas fontes: o OLTP de pedidos, a API da transportadora e os marts dbt. A transformação só pode rodar depois que todas as cargas terminarem. O `cron` não sabe expressar essa dependência de forma segura — não tem noção de "esperar a carga X terminar", nem de retry, nem de backfill. Entra o Airflow.

## Por que Airflow entra aqui

| Capacidade | Por que importa | Por que o cron não basta |
| --- | --- | --- |
| DAG (dependências) | A transformação espera as cargas. | cron só agenda horários, não dependências. |
| Retries | API externa falha de forma transitória. | cron não retenta com política. |
| Backfill | Reprocessar uma data específica. | cron não parametriza execução por data. |
| Logs por task | Saber o que falhou e onde. | cron joga tudo num log só. |

> O que fica **deliberadamente de fora**: Airflow **não processa nem consulta** dado. Ele agenda, ordena, retenta e faz backfill. Processar é trabalho do Spark/dbt; consultar é do Trino. Confundir esses papéis é erro clássico de entrevista.

## Status desta etapa

**Ambiente/documentação.** O compose sobe o Airflow em modo `standalone` para estudo. Os DAGs reais estão roteirizados no [BUILD.md](./BUILD.md).

## Conceitos

**DAG.** Um *Directed Acyclic Graph* descreve tarefas e suas dependências. O Airflow garante que uma task só roda quando as de que ela depende terminaram com sucesso.

**Idempotência e execução por data.** Cada run é parametrizada por uma data lógica (`data_interval`). Reprocessar uma data (backfill) deve produzir o mesmo resultado — o que só funciona se as tasks subjacentes (seeder, extractor, dbt) forem idempotentes, como construímos nos capítulos anteriores.

**Orquestração ≠ processamento.** O DAG chama os jobs que já existem (extração, carga, `dbt build`); ele não reimplementa a lógica deles.

> Aprofundamento técnico (scheduler, executors, sensors, XCom) em [`TECHNICAL.md`](./TECHNICAL.md).

## Como executar e como foi construído

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o Airflow e o BI opcional.
- **[BUILD.md](./BUILD.md)** — o roteiro do DAG que coordena OLTP, API externa e dbt, com retries e backfill.

## A dor que sobra

Com a orquestração resolvida, a próxima dor é **escala**: dados semi-estruturados (eventos de navegação, JSON) e volume alto estouram o warehouse relacional. Isso leva ao [capítulo 08](../08-data-lake-com-spark): Data Lake com Spark.

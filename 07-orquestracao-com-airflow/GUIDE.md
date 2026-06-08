# Cap. 07 — Orquestração com Airflow: coordenando pipelines

> **Aula deste capítulo.** Você aprende a coordenar jobs independentes com **Airflow** — DAGs, dependências, retries, backfill e observabilidade. A orientação está aqui; o código da DAG `nuvemstore_daily` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (scheduler, executor, parsing de DAG, por que Airflow orquestra mas não processa) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

Com OLTP, API externa e dbt, a plataforma tem três jobs independentes com dependências: dbt só deve rodar depois que ambas as ingestões terminaram. Se a API cai, dbt precisa esperar. Se o seeder falha, tudo para. Hoje isso é coordenado manualmente. Airflow automatiza: agendamento, dependências, retries, backfill e observabilidade.

## Pré-requisitos

- **Capítulo anterior:** 06 concluído (API externa ingerida).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### DAG: Directed Acyclic Graph

O Airflow organiza tarefas em DAGs — grafos sem ciclos. Uma tarefa pode depender de outra, mas a cadeia não pode voltar ao início. Isso garante que a execução tem uma ordem determinística.

**Exemplo trabalhado — por que "acíclico" não é detalhe.** A DAG da NuvemStore é `[ingest_oltp, ingest_api] >> run_dbt`: as duas ingestões rodam em paralelo, e o dbt só dispara quando *ambas* terminam. O Airflow consegue calcular essa ordem porque o grafo não tem ciclos — ele faz uma ordenação topológica e sabe que `run_dbt` vem depois. Se por engano você criasse `run_dbt >> ingest_oltp` *além* da aresta existente, teria um ciclo (`ingest → dbt → ingest`), e não existe "primeiro" — o Airflow recusa o DAG em vez de rodar para sempre. É a propriedade acíclica que torna "qual a ordem?" uma pergunta com resposta.

### Componentes do Airflow

- **Scheduler**: decide quais tarefas devem rodar baseado em schedule e dependências.
- **Webserver**: UI para visualizar DAGs, runs, logs e estados.
- **Metadata database**: Postgres interno que guarda estado de tudo.
- **Executor**: define onde tarefas rodam (Local, Celery, Kubernetes).

### Airflow como orquestrador, não processador

Airflow NÃO deve processar dados pesados dentro de si. O padrão saudável é ele disparar ferramentas externas: `BashOperator` para scripts, `DbtOperator` para dbt, `SparkSubmitOperator` para Spark. Se uma task faz JOIN de 1GB em memória no worker, a arquitetura está errada.

### Backfill e idempotência

Backfill permite reprocessar períodos passados — essencial quando um bug de transformação é descoberto 3 semanas depois. Mas backfill só é seguro quando as tarefas são **idempotentes**: rodar dia 15 de janeiro duas vezes deve produzir o mesmo resultado. Tudo que construímos até agora (TRUNCATE, DROP+CREATE, UPSERT) é idempotente by design.

**Exemplo trabalhado — o backfill que só funciona porque os jobs são idempotentes.** Dia 5 de fevereiro você descobre que o mart de receita estava errado desde 1º de janeiro. Com Airflow, você roda `dags backfill nuvemstore_daily -s 2024-01-01 -e 2024-02-04` e ele re-executa cada dia do intervalo. Isso só é seguro porque cada job reconstrói seu alvo do zero (TRUNCATE/DROP+CREATE) ou faz UPSERT por chave — re-rodar 15 de janeiro pela segunda vez dá exatamente o mesmo resultado da primeira. Se algum job fizesse `INSERT` puro, o backfill *somaria* dados sobre os antigos e você teria receita dobrada em metade do mês. Idempotência é a pré-condição que transforma backfill de "perigoso" em "rotineiro".

### TaskFlow API vs operators tradicionais

A TaskFlow API (`@task` decorator) simplifica DAGs simples em Python. Operators tradicionais (BashOperator, PythonOperator) dão mais controle. Para este capítulo, operators tradicionais são mais adequados porque os jobs já existem como scripts/containers separados.

---

## Etapa 1 — Criar o docker-compose.yml do Airflow

### Contexto
Airflow em Docker precisa de: webserver, scheduler, metadata database (Postgres), e opcionalmente um worker. O setup oficial usa o `docker-compose.yaml` da documentação, mas aqui fazemos um compose mais enxuto e educativo.

### Decisões de design
- *CeleryExecutor vs LocalExecutor*: LocalExecutor é suficiente para este capítulo — não precisamos de workers distribuídos.
- *Metadata database*: Postgres separado do OLTP — o Airflow tem seu próprio banco.
- *Volumes montados*: `./airflow/dags` para os DAGs, logs em volume nomeado.

### O que fazer
Compose com: `airflow-init` (roda `airflow db init`), `airflow-webserver` (porta 8080), `airflow-scheduler`, `postgres-airflow` (metadata), `oltp` (fonte), `api-mock` (fonte).

### ⚠️ Armadilhas
- Airflow 2.x exige `airflow db init` antes de qualquer coisa. Sem o init, scheduler e webserver falham silenciosamente.
- Não definir `AIRFLOW__CORE__FERNET_KEY`: warnings de segurança nos logs.
- Dar pouca memória ao scheduler: DAGs grandes travam.

---

## Etapa 2 — Criar a DAG principal

### Contexto
A DAG coordena: (1) ingerir OLTP, (2) ingerir API externa, (3) rodar dbt. As ingestões podem rodar em paralelo; dbt espera ambas terminarem.

### Decisões de design
- *Schedule diário*: `schedule_interval='@daily'`. Simula um pipeline batch recorrente.
- *Retries*: 2 retries com delay de 5 minutos para tarefas de ingestão (falhas de rede são transitórias).
- *Dependências*: `[ingest_oltp, ingest_api] >> run_dbt`. Notação bitshift do Airflow.
- *Catchup desabilitado*: `catchup=False` para não reprocessar todo o histórico ao ati
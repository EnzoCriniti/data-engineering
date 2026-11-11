# Cap. 07 — Orquestração com Airflow: coordenando pipelines

> **Aula deste capítulo.** Você aprende a coordenar jobs independentes com **Airflow** — DAGs, dependências, retries, backfill e observabilidade. A orientação está aqui; o link para a DAG `nuvemstore_daily` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (scheduler, executor, parsing de DAG, por que Airflow orquestra mas não processa) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

Com OLTP, API externa e dbt, a plataforma tem três jobs independentes com dependências: dbt só deve rodar depois que ambas as ingestões terminaram. Se a API cai, dbt precisa esperar. Se o seeder falha, tudo para. Hoje isso é coordenado manualmente. Airflow automatiza: agendamento, dependências, retries, backfill e observabilidade.

## Pré-requisitos

- **Capítulo anterior:** 06 concluído (API externa ingerida).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### DAG: Directed Acyclic Graph

O Airflow organiza tarefas em DAGs — grafos sem ciclos. Uma tarefa pode depender de outra, mas a cadeia não pode voltar ao início. Isso garante que a execução tem uma ordem determinística.

**Exemplo trabalhado — por que "acíclico" não é detalhe.** A cadeia de carga da NuvemStore é `carga_oltp >> carga_api >> dbt_build`. O dbt dispara depois das duas ingestões. O Airflow consegue calcular essa ordem porque o grafo não tem ciclos — ele faz uma ordenação topológica e sabe que `run_dbt` vem depois. Se por engano você criasse `dbt_build >> carga_oltp` *além* da aresta existente, teria um ciclo (`ingest → dbt → ingest`), e não existe "primeiro" — o Airflow recusa o DAG em vez de rodar para sempre. É a propriedade acíclica que torna "qual a ordem?" uma pergunta com resposta.

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
O ambiente deste capítulo usa o scheduler com LocalExecutor e um PostgreSQL de metadados. A CLI consulta o estado das execuções.

### Decisões de design
- *CeleryExecutor vs LocalExecutor*: LocalExecutor é suficiente para este capítulo — não precisamos de workers distribuídos.
- *Metadata database*: Postgres separado do OLTP — o Airflow tem seu próprio banco.
- *Volumes montados*: logs e metadados em volumes nomeados. A imagem inclui o DAG.

### O que fazer
O Compose inclui `airflow-init` para executar `airflow db migrate`, `airflow-scheduler` para executar as tarefas e `airflow-db` para os metadados.

### ⚠️ Armadilhas
- O scheduler depende da migração bem-sucedida dos metadados.
- Dar pouca memória ao scheduler: DAGs grandes travam.

---

## Etapa 2 — Criar a DAG principal

### Contexto
A DAG coordena: (1) ingerir OLTP, (2) ingerir API externa, (3) rodar dbt. As duas cargas escrevem no mesmo DuckDB e executam em sequência.

### Decisões de design
- *Schedule diário*: `schedule='0 6 * * *'` em UTC. Simula um pipeline batch recorrente.
- *Retries*: 2 retries com espera configurável para tarefas de ingestão (falhas de rede são transitórias).
- *Dependências*: `carga_oltp >> carga_api >> dbt_build`. Notação bitshift do Airflow.
- *Catchup desabilitado*: `catchup=False` para não reprocessar todo o histórico ao ativar a DAG.

### O que fazer
`airflow/dags/nuvemstore_daily.py` chama os scripts de simulação, carga OLTP, carga API, build dbt e verificação de SLA. Em backfill, passa o intervalo lógico para o extractor.

### ⚠️ Armadilhas
- `BashOperator` sem `set -e` no script: falhas silenciosas — o operador retorna success mesmo se um comando intermediário falhou.
- Importar módulos pesados no topo do arquivo da DAG: o scheduler parseia todos os DAGs periodicamente — imports lentos degradam performance.
- Não definir `start_date` com data fixa: usar `datetime.now()` faz a DAG recriar runs fantasmas.

### 📚 Para se aprofundar
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) — padrões recomendados.
- [Airflow TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html) — abordagem moderna com decorators.

---

## ✅ Checklist final

- [ ] O Compose sobe o scheduler após a migração dos metadados
- [ ] DAG `nuvemstore_daily` aparece em `airflow dags list`
- [ ] Trigger manual executa as cinco tarefas em ordem
- [ ] O dbt só roda após as duas cargas
- [ ] Os logs das tarefas persistem no volume `airflow-logs`
- [ ] Re-trigger da mesma run produz o mesmo resultado (idempotência)

Compreensão (você entendeu — responda sem olhar):

- [ ] O que a propriedade **acíclica** garante? Dê um exemplo de aresta que criaria um ciclo na DAG da NuvemStore.
- [ ] Por que Airflow deve **orquestrar** e não **processar** dados pesados? O que indica que a arquitetura está errada?
- [ ] Por que backfill só é seguro se as tarefas forem idempotentes? O que `INSERT` puro causaria num backfill de meio mês?
- [ ] Por que `start_date` deve ser data fixa e não `datetime.now()`?

## A dor que sobra

O pipeline inteiro opera em batch — dados só ficam disponíveis após a execução diária. Volumes crescentes tornam o full reload cada vez mais lento. O capítulo 08 muda de paradigma: sai de tabelas de banco para arquivos distribuídos em um data lake com Spark.

# Complemento técnico — Apache Airflow e orquestração

## O que este capítulo aprofunda

Este capítulo trata da coordenacao de pipelines. A pergunta deixa de ser "como transformar dados?" e passa a ser "quando, em que ordem, com quais retries e com qual observabilidade?".

## Pequena história

O Airflow foi criado no Airbnb por volta de 2014 para lidar com muitos workflows de dados definidos em código. Depois entrou no ecossistema Apache e se tornou uma das ferramentas mais conhecidas de orquestracao batch.

Ele se popularizou porque substituiu cron e scripts encadeados por DAGs declarativos em Python, com UI, histórico de execucoes, logs e retries.

## Por baixo dos panos

Airflow organiza trabalho em DAGs, Directed Acyclic Graphs. Um DAG e um grafo sem ciclos: uma tarefa pode depender de outra, mas a cadeia não pode voltar para o inicio.

Componentes principais:

- Scheduler: decide quais tarefas devem rodar.
- Webserver: UI para operadores e engenheiros.
- Metadata database: guarda estado de DAGs, runs, tarefas, logs e configuracoes.
- Executor: define onde as tarefas rodam.
- Workers: executam tarefas em setups distribuidos.

Airflow não deve processar dados pesados dentro do próprio processo da task. O padrão saudavel e ele disparar ferramentas externas: dbt, Spark, scripts, APIs, containers ou jobs Kubernetes.

## Conceitos operacionais

Backfill permite reprocessar periodos passados. Isso só e seguro quando as tarefas são idempotentes.

Retries ajudam com falhas transitorias, como API fora do ar. Mas retry não corrige erro deterministico de código ou dado ruim.

SLA e alertas transformam pipeline em operação. A pergunta deixa de ser "rodou?" e passa a ser "rodou dentro do esperado?".

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Dagster | Orquestrador moderno, forte em assets e tipagem de dependencias. |
| Prefect | Experiencia Python fluida, boa para workflows dinamicos. |
| Luigi | Mais antigo, simples, com menos plataforma ao redor. |
| Argo Workflows | Kubernetes-native, forte para containers. |
| cron | Simples, mas sem DAG, histórico rico, retries e backfill nativos. |

## Quando usar

Use Airflow quando ha muitas tarefas batch, dependencias claras, necessidade de agendamento, histórico e reprocessamento.

Evite transformar Airflow em motor de processamento. Se uma task faz join gigante em memória dentro do worker, a arquitetura está errada; ela deveria disparar Spark, dbt ou outro motor adequado.

## Como isso aparece no projeto

No capítulo 07, dbt vira uma tarefa dentro de um DAG. O Airflow coordena ingestao de múltiplas fontes e garante que transformacoes só rodem depois que as dependencias estiverem prontas.

## 📚 Referências

- [Apache Airflow Documentation](https://airflow.apache.org/docs/) — referência oficial com guia de conceitos, operadores e configuração.
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html) — padrões recomendados para DAGs de produção.
- [Dagster Documentation](https://docs.dagster.io/) — orquestrador moderno com foco em assets e observabilidade.

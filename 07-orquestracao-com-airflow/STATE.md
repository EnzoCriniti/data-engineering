# Gabarito de estado - Capitulo 07

## Objetivo do capitulo

Orquestrar o pipeline existente com Airflow, adicionando dependencias, retries, logs e backfill.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 06:

- origem populada;
- raw tables carregadas;
- transformacoes dbt implementadas;
- testes dbt disponiveis.

## Etapas do capitulo

1. Subir Airflow.
2. Criar DAG principal do pipeline.
3. Adicionar tasks para seed/extracao/carga quando necessario.
4. Adicionar task `dbt run`.
5. Adicionar task `dbt test`.
6. Configurar retries e logs.
7. Parametrizar execucao por data.

## Estado final esperado

Ao final, deve existir:

- DAG versionado;
- execucao manual substituida por execucao orquestrada;
- historico de runs no Airflow;
- logs por task;
- possibilidade de reprocessar uma janela.

## Validacoes

- DAG aparece na UI do Airflow.
- Run completo termina com sucesso.
- Falha em uma task nao executa dependentes indevidos.
- Retry funciona em uma falha simulada.
- Resultado final bate com execucao manual/dbt.

## Como o proximo capitulo usa este estado

O capitulo 08 parte de uma plataforma orquestrada, mas com limite de escala e rigidez para dados semi-estruturados. O proximo passo e introduzir data lake com Spark.

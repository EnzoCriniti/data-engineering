# Gabarito de estado - Capítulo 07

## Objetivo do capítulo

Orquestrar o pipeline existente com Airflow, adicionando dependencias, retries, logs e backfill.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 06:

- origem populada;
- raw tables carregadas;
- transformacoes dbt implementadas;
- testes dbt disponíveis.

## Etapas do capítulo

1. Subir Airflow.
2. Criar DAG principal do pipeline.
3. Adicionar tasks para seed/extracao/carga quando necessário.
4. Adicionar task `dbt run`.
5. Adicionar task `dbt test`.
6. Configurar retries e logs.
7. Parametrizar execução por data.

## Estado final esperado

Ao final, deve existir:

- DAG versionado;
- execução manual substituida por execução orquestrada;
- histórico de runs no Airflow;
- logs por task;
- possibilidade de reprocessar uma janela.

## Validações

- DAG aparece na UI do Airflow.
- Run completo termina com sucesso.
- Falha em uma task não executa dependentes indevidos.
- Retry funciona em uma falha simulada.
- Resultado final bate com execução manual/dbt.

## Como o proximo capítulo usa este estado

O capítulo 08 parte de uma plataforma orquestrada, mas com limite de escala e rigidez para dados semi-estruturados. O proximo passo e introduzir data lake com Spark.

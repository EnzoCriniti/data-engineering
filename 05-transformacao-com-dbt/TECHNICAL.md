# Complemento tecnico - dbt e transformacao como codigo

## O que este capitulo aprofunda

Este capitulo troca SQL solto por transformacao versionada, testavel e documentada. dbt nao extrai dados e nao orquestra sozinho; ele organiza a camada de transformacao dentro do ambiente analitico.

## Pequena historia

O dbt surgiu na segunda metade da decada de 2010, no contexto de warehouses cloud e ELT. A ideia central era simples: se a transformacao agora acontece dentro do banco, entao SQL deve ser tratado como codigo de software, com dependencias, testes, documentacao e deploy.

Ele cresceu junto com Snowflake, BigQuery, Redshift e Databricks, mas tambem funciona em ambientes locais com adaptadores como Postgres e DuckDB.

## Por baixo dos panos

Um projeto dbt e composto por modelos SQL. Cada modelo normalmente vira uma view ou tabela no destino.

O `ref()` e o ponto central. Em vez de escrever o nome fisico de uma tabela, um modelo referencia outro modelo pelo nome logico. Com isso, o dbt monta um DAG de dependencias e executa na ordem correta.

Testes de dados sao consultas que devem retornar zero linhas problematicas. Exemplos:

- `not_null`: coluna obrigatoria.
- `unique`: chave sem duplicidade.
- `relationships`: FK logica entre modelos.
- testes customizados: regras especificas de negocio.

Materializacoes definem como o modelo vira objeto no banco:

- view: sempre recalcula na leitura.
- table: calcula e persiste.
- incremental: processa apenas dados novos ou alterados.

## O que dbt nao e

dbt nao e um orquestrador completo. Ele sabe a ordem dos modelos, mas nao substitui Airflow, Dagster ou Prefect quando ha multiplas fontes, sensores, retries externos e dependencias entre sistemas.

dbt tambem nao e ferramenta de ingestao. Ele espera que os dados ja estejam no destino analitico ou em uma camada raw acessivel.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| SQLMesh | Parecido com dbt, com foco forte em ambientes e planejamento. |
| Dataform | Transformacao SQL como codigo, integrado ao ecossistema Google. |
| Stored procedures | Podem transformar dados, mas tendem a ter menos lineage e controle moderno. |
| Spark SQL jobs | Mais flexiveis para escala, mas exigem mais engenharia. |
| Coalesce | Plataforma visual para transformacoes, comum em Snowflake. |

## Quando usar

Use dbt quando a maior parte da transformacao pode ser expressa em SQL e o time precisa de confiabilidade, testes e documentacao.

Evite usar dbt para processamento pesado fora do banco, ingestao de APIs, streaming ou logica procedural complexa. Nesses casos, ele deve ser uma etapa dentro de uma arquitetura maior.

## Como isso aparece no projeto

O capitulo 05 reaproveita a dor do capitulo 04: SQL manual demais. A mudanca arquitetural e colocar transformacoes em modelos com dependencias explicitas, testes e documentacao gerada.

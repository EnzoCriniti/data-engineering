# Complemento técnico — dbt e transformação como código

## O que este capítulo aprofunda

Este capítulo troca SQL solto por transformacao versionada, testavel e documentada. dbt não extrai dados e não orquestra sozinho; ele organiza a camada de transformacao dentro do ambiente analítico.

## Pequena história

O dbt surgiu na segunda metade da década de 2010, no contexto de warehouses cloud e ELT. A ideia central era simples: se a transformacao agora acontece dentro do banco, então SQL deve ser tratado como código de software, com dependencias, testes, documentacao e deploy.

Ele cresceu junto com Snowflake, BigQuery, Redshift e Databricks, mas também funciona em ambientes locais com adaptadores como Postgres e DuckDB.

## Por baixo dos panos

Um projeto dbt e composto por modelos SQL. Cada modelo normalmente vira uma view ou tabela no destino.

O `ref()` e o ponto central. Em vez de escrever o nome físico de uma tabela, um modelo referência outro modelo pelo nome lógico. Com isso, o dbt monta um DAG de dependencias e executa na ordem correta.

Testes de dados são consultas que devem retornar zero linhas problematicas. Exemplos:

- `not_null`: coluna obrigatoria.
- `unique`: chave sem duplicidade.
- `relationships`: FK lógica entre modelos.
- testes customizados: regras especificas de negócio.

Materializacoes definem como o modelo vira objeto no banco:

- view: sempre recalcula na leitura.
- table: calcula e persiste.
- incremental: processa apenas dados novos ou alterados.

## O que dbt não e

dbt não e um orquestrador completo. Ele sabe a ordem dos modelos, mas não substitui Airflow, Dagster ou Prefect quando ha múltiplas fontes, sensores, retries externos e dependencias entre sistemas.

dbt também não e ferramenta de ingestao. Ele espera que os dados já estejam no destino analítico ou em uma camada raw acessivel.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| SQLMesh | Parecido com dbt, com foco forte em ambientes e planejamento. |
| Dataform | Transformacao SQL como código, integrado ao ecossistema Google. |
| Stored procedures | Podem transformar dados, mas tendem a ter menos lineage e controle moderno. |
| Spark SQL jobs | Mais flexíveis para escala, mas exigem mais engenharia. |
| Coalesce | Plataforma visual para transformacoes, comum em Snowflake. |

## Quando usar

Use dbt quando a maior parte da transformacao pode ser expressa em SQL e o time precisa de confiabilidade, testes e documentacao.

Evite usar dbt para processamento pesado fora do banco, ingestao de APIs, streaming ou lógica procedural complexa. Nesses casos, ele deve ser uma etapa dentro de uma arquitetura maior.

## Como isso aparece no projeto

O capítulo 05 reaproveita a dor do capítulo 04: SQL manual demais. A mudança arquitetural e colocar transformacoes em modelos com dependencias explicitas, testes e documentacao gerada.

## 📚 Referências

- [dbt Documentation](https://docs.getdbt.com/) — referência oficial com guias de materialização, testes e packages.
- [dbt Best Practices](https://docs.getdbt.com/best-practices) — convenções de projeto recomendadas pela dbt Labs.
- [SQLMesh Documentation](https://sqlmesh.readthedocs.io/) — alternativa moderna ao dbt com foco em ambientes e planejamento.

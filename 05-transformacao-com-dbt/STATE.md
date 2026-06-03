# Gabarito de estado - Capitulo 05

## Objetivo do capitulo

Substituir transformacoes SQL manuais por um projeto dbt com modelos, testes, documentacao e lineage.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 04:

- origem OLTP populada;
- dados raw carregados no destino analitico;
- marts manuais usados como referencia.

## Etapas do capitulo

1. Subir ambiente com destino analitico.
2. Recriar raw tables a partir do pipeline anterior.
3. Criar projeto dbt.
4. Implementar modelos `staging`.
5. Implementar modelos `marts`.
6. Adicionar testes em `schema.yml`.
7. Gerar docs e lineage.

## Estado final esperado

Ao final, deve existir:

- projeto dbt versionado;
- modelos staging e marts;
- testes de dados passando;
- marts dbt equivalentes aos marts manuais;
- documentacao dbt gerada.

## Validacoes

- `dbt run` executa sem erro.
- `dbt test` passa.
- Receita diaria dbt bate com receita diaria manual.
- Top produtos dbt bate com top produtos manual.
- O lineage mostra dependencias entre raw, staging e marts.

## Como o proximo capitulo usa este estado

O capitulo 06 adiciona uma fonte externa batch. Depois disso, o capitulo 07 passa a orquestrar carga, API e transformacoes com Airflow.

# Gabarito de estado - Capitulo 04

## Objetivo do capitulo

Implementar o primeiro ELT batch com Python: extrair do OLTP, carregar raw no destino analitico e criar marts.

## Estado inicial

O capitulo recria:

- origem OLTP populada;
- separacao entre origem e area analitica;
- necessidade de mover dados sem consultar analytics direto no banco transacional.

## Etapas do capitulo

1. Subir Postgres OLTP.
2. Popular a origem com `seeder`.
3. Executar pipeline Python.
4. Carregar tabelas raw no DuckDB.
5. Criar marts de receita diaria e top produtos.

## Estado final esperado

Ao final, deve existir:

- OLTP populado;
- arquivo DuckDB em `data/warehouse/nuvemstore.duckdb`;
- tabelas `raw_*`;
- `mart_receita_diaria`;
- `mart_top_produtos`.

## Validacoes

- Quantidade de linhas raw bate com a origem.
- Receita dos marts bate com a soma dos itens de pedidos nao cancelados.
- Rodar o pipeline novamente nao duplica resultados.
- O DuckDB pode ser inspecionado localmente.

## Como o proximo capitulo usa este estado

O capitulo 05 usa os marts manuais como gabarito. dbt deve recriar os mesmos resultados com modelos, testes e lineage.

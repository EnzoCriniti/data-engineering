# Gabarito de estado - Capítulo 04

## Objetivo do capítulo

Implementar o primeiro ELT batch com Python: extrair do OLTP, carregar raw no destino analítico e criar marts.

## Estado inicial

O capítulo recria:

- origem OLTP populada;
- separacao entre origem e área analítica;
- necessidade de mover dados sem consultar analytics direto no banco transacional.

## Etapas do capítulo

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

## Validações

- Quantidade de linhas raw bate com a origem.
- Receita dos marts bate com a soma dos itens de pedidos não cancelados.
- Rodar o pipeline novamente não duplica resultados.
- O DuckDB pode ser inspecionado localmente.

## Como o proximo capítulo usa este estado

O capítulo 05 usa os marts manuais como gabarito. dbt deve recriar os mesmos resultados com modelos, testes e lineage.

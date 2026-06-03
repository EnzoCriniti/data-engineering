# Gabarito de estado - Capitulo 02

## Objetivo do capitulo

Mostrar a primeira solucao pragmatica: criar a area analitica dentro do mesmo banco OLTP, em outro schema.

## Estado inicial

O capitulo recria:

- schema OLTP do capitulo 00;
- dados sinteticos populados pelo seeder;
- modelo dimensional conceitual do capitulo 01.

## Etapas do capitulo

1. Subir um unico Postgres.
2. Criar tabelas OLTP no schema principal.
3. Criar schema `analytics`.
4. Criar tabelas dimensionais em `analytics`.
5. Popular a origem com o seeder compartilhado.

## Estado final esperado

Ao final, o mesmo Postgres deve conter:

- tabelas transacionais no schema principal;
- tabelas analiticas no schema `analytics`;
- origem populada;
- separacao logica entre aplicacao e analytics, mas sem isolamento fisico.

## Validacoes

- `public` contem tabelas OLTP.
- `analytics` contem dimensoes e fato.
- O seeder popula a origem.
- A arquitetura deixa claro que os recursos fisicos continuam compartilhados.

## Como o proximo capitulo usa este estado

O capitulo 03 parte da dor deste estado: schemas separados nao isolam CPU, memoria, I/O e conexoes. O proximo capitulo separa OLTP e warehouse em bancos diferentes.

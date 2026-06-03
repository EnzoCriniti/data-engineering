# Gabarito de estado - Capítulo 02

## Objetivo do capítulo

Mostrar a primeira solucao pragmatica: criar a área analítica dentro do mesmo banco OLTP, em outro schema.

## Estado inicial

O capítulo recria:

- schema OLTP do capítulo 00;
- dados sintéticos populados pelo seeder;
- modelo dimensional conceitual do capítulo 01.

## Etapas do capítulo

1. Subir um único Postgres.
2. Criar tabelas OLTP no schema principal.
3. Criar schema `analytics`.
4. Criar tabelas dimensionais em `analytics`.
5. Popular a origem com o seeder compartilhado.

## Estado final esperado

Ao final, o mesmo Postgres deve conter:

- tabelas transacionais no schema principal;
- tabelas analíticas no schema `analytics`;
- origem populada;
- separacao lógica entre aplicação e analytics, mas sem isolamento físico.

## Validações

- `public` contem tabelas OLTP.
- `analytics` contem dimensoes e fato.
- O seeder popula a origem.
- A arquitetura deixa claro que os recursos físicos continuam compartilhados.

## Como o proximo capítulo usa este estado

O capítulo 03 parte da dor deste estado: schemas separados não isolam CPU, memória, I/O e conexões. O proximo capítulo separa OLTP e warehouse em bancos diferentes.

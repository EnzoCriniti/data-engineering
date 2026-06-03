# Gabarito de estado - Capítulo 03

## Objetivo do capítulo

Separar fisicamente a origem OLTP e o warehouse analítico.

## Estado inicial

O capítulo recria:

- origem OLTP do capítulo 00;
- modelo dimensional do capítulo 01;
- dor do capítulo 02: analytics dividindo recursos com o transacional.

## Etapas do capítulo

1. Subir Postgres `oltp`.
2. Subir Postgres `warehouse`.
3. Popular o OLTP com o seeder.
4. Criar schema dimensional no warehouse.
5. Executar job de migracao/materializacao.

## Estado final esperado

Ao final, devem existir dois bancos separados:

- `oltp`: fonte transacional populada;
- `warehouse`: tabelas `analytics.dim_*` e `analytics.fct_vendas` populadas;
- carga inicial materializada do OLTP para o warehouse.

## Validações

- `oltp` tem clientes, produtos, pedidos e itens.
- `warehouse` tem dimensoes e fato populadas.
- A contagem de itens vendidos no warehouse bate com pedidos não cancelados da origem.
- A receita agregada no warehouse bate com a origem para o mesmo filtro.

## Como o proximo capítulo usa este estado

O capítulo 04 parte da existencia de origem e destino separados para mostrar o primeiro ELT batch com Python de extracao, carga e transformacao.

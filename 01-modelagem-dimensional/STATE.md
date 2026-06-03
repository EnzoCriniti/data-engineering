# Gabarito de estado - Capítulo 01

## Objetivo do capítulo

Desenhar o modelo analítico alvo a partir da origem OLTP do capítulo 00.

## Estado inicial

Este capítulo assume o modelo transacional do capítulo 00:

- cliente;
- produto;
- categoria;
- pedido;
- item_pedido;
- pagamento;
- entrega;
- entregador.

## Etapas do capítulo

1. Definir o grão da fato de vendas.
2. Desenhar dimensoes principais: tempo, cliente, produto e loja/regiao quando aplicavel.
3. Definir surrogate keys.
4. Explicar SCD, principalmente SCD Tipo 2 para cliente.
5. Contrastar star schema e snowflake.

## Estado final esperado

Ao final, deve existir um desenho claro do modelo OLAP:

- fato de vendas definida;
- dimensoes definidas;
- grão documentado;
- justificativa de desnormalizacao;
- ponte conceitual OLTP -> OLAP.

## Validações

- Cada métrica tem grão claro.
- Cada dimensao tem papel analítico.
- O modelo responde perguntas como receita por data, produto, categoria e cliente.
- O modelo não mistura grãos diferentes na mesma fato.

## Como o proximo capítulo usa este estado

O capítulo 02 materializa a ideia dimensional dentro do mesmo banco transacional para mostrar a primeira solucao comum e sua limitacao operacional.

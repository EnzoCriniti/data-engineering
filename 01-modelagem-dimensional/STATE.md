# Gabarito de estado - Capitulo 01

## Objetivo do capitulo

Desenhar o modelo analitico alvo a partir da origem OLTP do capitulo 00.

## Estado inicial

Este capitulo assume o modelo transacional do capitulo 00:

- cliente;
- produto;
- categoria;
- pedido;
- item_pedido;
- pagamento;
- entrega;
- entregador.

## Etapas do capitulo

1. Definir o grao da fato de vendas.
2. Desenhar dimensoes principais: tempo, cliente, produto e loja/regiao quando aplicavel.
3. Definir surrogate keys.
4. Explicar SCD, principalmente SCD Tipo 2 para cliente.
5. Contrastar star schema e snowflake.

## Estado final esperado

Ao final, deve existir um desenho claro do modelo OLAP:

- fato de vendas definida;
- dimensoes definidas;
- grao documentado;
- justificativa de desnormalizacao;
- ponte conceitual OLTP -> OLAP.

## Validacoes

- Cada metrica tem grao claro.
- Cada dimensao tem papel analitico.
- O modelo responde perguntas como receita por data, produto, categoria e cliente.
- O modelo nao mistura graos diferentes na mesma fato.

## Como o proximo capitulo usa este estado

O capitulo 02 materializa a ideia dimensional dentro do mesmo banco transacional para mostrar a primeira solucao comum e sua limitacao operacional.

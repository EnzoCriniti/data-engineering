# Gabarito de estado - Capitulo 00

## Objetivo do capitulo

Definir a origem transacional da NuvemStore: um modelo OLTP normalizado, consistente e populavel com dados sinteticos.

## Estado inicial

Nao ha ambiente anterior. Este e o ponto zero da trilha.

## Etapas do capitulo

1. Definir o schema OLTP em `ddl/schema.sql`.
2. Criar tabelas normalizadas: cliente, categoria, produto, pedido, item_pedido, pagamento, entrega e entregador.
3. Garantir PKs, FKs, checks e constraints basicas.
4. Criar seeder com dados sinteticos coerentes.
5. Permitir reset idempotente da origem.

## Estado final esperado

Ao final, deve existir uma origem transacional reproduzivel:

- schema OLTP versionado;
- seeder executavel;
- dados de clientes, produtos, pedidos, pagamentos e entregas;
- dominio suficiente para alimentar analytics, CDC e streaming nos capitulos seguintes.

## Validacoes

- O schema cria sem erro em Postgres.
- O seeder executa mais de uma vez com `SEED_RESET=true`.
- As tabelas principais ficam populadas.
- FKs impedem dados orfaos.

## Como o proximo capitulo usa este estado

O capitulo 01 usa este modelo como origem conceitual para desenhar o modelo dimensional. As tabelas transacionais viram a base para fatos e dimensoes.

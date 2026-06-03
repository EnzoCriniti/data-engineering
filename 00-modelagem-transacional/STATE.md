# Gabarito de estado - Capítulo 00

## Objetivo do capítulo

Definir a origem transacional da NuvemStore: um modelo OLTP normalizado, consistente e populavel com dados sintéticos.

## Estado inicial

Não ha ambiente anterior. Este e o ponto zero da trilha.

## Etapas do capítulo

1. Definir o schema OLTP em `ddl/schema.sql`.
2. Criar tabelas normalizadas: cliente, categoria, produto, pedido, item_pedido, pagamento, entrega e entregador.
3. Garantir PKs, FKs, checks e constraints basicas.
4. Criar seeder com dados sintéticos coerentes.
5. Permitir reset idempotente da origem.

## Estado final esperado

Ao final, deve existir uma origem transacional reproduzivel:

- schema OLTP versionado;
- seeder executavel;
- dados de clientes, produtos, pedidos, pagamentos e entregas;
- domínio suficiente para alimentar analytics, CDC e streaming nos capítulos seguintes.

## Validações

- O schema cria sem erro em Postgres.
- O seeder executa mais de uma vez com `SEED_RESET=true`.
- As tabelas principais ficam populadas.
- FKs impedem dados orfaos.

## Como o proximo capítulo usa este estado

O capítulo 01 usa este modelo como origem conceitual para desenhar o modelo dimensional. As tabelas transacionais viram a base para fatos e dimensoes.

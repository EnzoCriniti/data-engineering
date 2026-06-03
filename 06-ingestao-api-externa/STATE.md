# Gabarito de estado - Capitulo 06

## Objetivo do capitulo

Adicionar uma fonte externa batch, simulando uma transportadora, e carregar seus dados em staging no warehouse.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 05:

- origem interna ja modelada;
- pipeline e transformacoes internas existentes;
- marts internos disponiveis;
- necessidade de enriquecer analytics com uma fonte externa.

## Etapas do capitulo

1. Subir API fake da transportadora.
2. Subir warehouse/staging.
3. Definir contrato do endpoint.
4. Implementar extractor batch.
5. Carregar `staging.transportadora_entregas`.
6. Controlar incremental por `atualizado_em`.
7. Garantir idempotencia por `entrega_id`.

## Estado final esperado

Ao final, deve existir:

- API externa simulada;
- staging de entregas externas;
- carga batch reproduzivel;
- checkpoint incremental;
- dados prontos para cruzar com pedidos internos.

## Validacoes

- API responde com payload JSON.
- Carga popula `staging.transportadora_entregas`.
- Rodar a carga duas vezes nao duplica entregas.
- Registros novos por `atualizado_em` entram corretamente.
- `pedido_id` externo pode ser reconciliado com pedido interno.

## Como o proximo capitulo usa este estado

O capitulo 07 usa este estado para justificar Airflow: agora ha OLTP interno, transformacoes dbt e API externa batch que precisam rodar em ordem, com retries e backfill.

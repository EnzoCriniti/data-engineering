# Gabarito de estado - Capitulo 13

## Objetivo do capitulo

Preparar uma tabela de features para um modelo simples de deteccao de fraude de pagamentos.

## Estado inicial

O capitulo deve recriar o estado final dos capitulos anteriores:

- lakehouse com gold historica;
- CDC de pagamentos;
- metricas streaming recentes;
- fonte externa de logistica disponivel;
- necessidade de combinar sinais historicos e recentes.

## Etapas do capitulo

1. Definir entidade de predicao: pagamento.
2. Definir label de fraude ou proxy inicial.
3. Criar tabela de features.
4. Materializar features historicas batch.
5. Incorporar features recentes vindas do streaming.
6. Separar dataset de treino e dataset de scoring.
7. Validar point-in-time correctness.

## Estado final esperado

Ao final, deve existir:

- `ml.fraude_pagamento_features`;
- chave por pagamento;
- timestamp de feature;
- colunas de features historicas;
- colunas de features recentes;
- label opcional para treino;
- base pronta para um modelo simples.

## Validacoes

- Nao ha duplicidade por `pagamento_id`.
- Features nao usam informacao futura.
- Linhas de scoring nao exigem label.
- Distribuicao de features e monitoravel.
- A tabela pode ser recriada de forma idempotente.

## Como a trilha fecha este estado

Este estado mostra que a plataforma tambem pode servir uma base de ML, combinando historico batch, CDC, streaming e dados de fontes externas.

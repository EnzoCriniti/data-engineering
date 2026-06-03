# Gabarito de estado - Capítulo 13

## Objetivo do capítulo

Preparar uma tabela de features para um modelo simples de detecção de fraude de pagamentos.

## Estado inicial

O capítulo deve recriar o estado final dos capítulos anteriores:

- lakehouse com gold histórica;
- CDC de pagamentos;
- métricas streaming recentes;
- fonte externa de logística disponível;
- necessidade de combinar sinais históricos e recentes.

## Etapas do capítulo

1. Definir entidade de predicao: pagamento.
2. Definir label de fraude ou proxy inicial.
3. Criar tabela de features.
4. Materializar features históricas batch.
5. Incorporar features recentes vindas do streaming.
6. Separar dataset de treino e dataset de scoring.
7. Validar point-in-time correctness.

## Estado final esperado

Ao final, deve existir:

- `ml.fraude_pagamento_features`;
- chave por pagamento;
- timestamp de feature;
- colunas de features históricas;
- colunas de features recentes;
- label opcional para treino;
- base pronta para um modelo simples.

## Validações

- Não ha duplicidade por `pagamento_id`.
- Features não usam informacao futura.
- Linhas de scoring não exigem label.
- Distribuicao de features e monitoravel.
- A tabela pode ser recriada de forma idempotente.

## Como a trilha fecha este estado

Este estado mostra que a plataforma também pode servir uma base de ML, combinando histórico batch, CDC, streaming e dados de fontes externas.

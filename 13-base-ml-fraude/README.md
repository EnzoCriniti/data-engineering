# Capitulo 13 - Base de ML para fraude de pagamentos

> De onde viemos: a plataforma ja tem batch, API externa, lake/lakehouse, CDC e streaming. Agora o objetivo e preparar uma base analitica para um modelo simples de fraude.

## Cenario de negocio

A NuvemStore quer detectar pagamentos suspeitos. O modelo nao precisa ser complexo no inicio; o ponto do capitulo e mostrar como preparar dados confiaveis para ML.

As features podem combinar:

- dados transacionais de pagamento e pedido;
- historico do cliente no lakehouse;
- ocorrencias logisticas da API externa;
- metricas quase em tempo real vindas do streaming.

## Status desta etapa

Status atual: **ambiente base/documentacao**.

O compose sobe um Postgres simples como base de features local. No futuro, essa tabela pode ser materializada no lakehouse ou em uma feature store dedicada.

## Como esta etapa migra a anterior

Esta etapa nao cria uma nova fonte. Ela prepara uma visao de ML a partir das fontes que a plataforma ja tem.

Plano de migracao:

1. usar gold do lakehouse como base historica;
2. trazer atualizacoes de pagamento capturadas por CDC;
3. incorporar metricas recentes do streaming;
4. gerar `ml.fraude_pagamento_features`;
5. separar colunas de feature, label e timestamp;
6. validar que treino e scoring usam a mesma definicao de features.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

## Conceitos principais

- Feature table.
- Training dataset vs scoring dataset.
- Label leakage.
- Point-in-time correctness.
- Batch features vs real-time features.
- Monitoramento de drift e qualidade de features.

## A dor que sobra

Depois de preparar uma base de ML, a trilha fecha mostrando que a plataforma tambem pode servir produtos analiticos avancados, nao apenas dashboards.

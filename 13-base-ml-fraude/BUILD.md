# Build — Capítulo 13: como construir a base de ML para fraude

> Guia **avançado e detalhado**. Status **ambiente base / documentação**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Montar uma feature table confiável para detecção de fraude de pagamentos, consolidando os sinais que a plataforma já produz (batch, CDC, streaming), com point-in-time correctness e sem label leakage. O foco é a engenharia de dados para ML, não o modelo.

## Pré-requisitos de conhecimento

- As fontes da trilha: gold do lakehouse ([cap. 10](../10-lakehouse-medallion)), mudanças via CDC ([cap. 11](../11-cdc-com-debezium)), métricas de streaming ([cap. 12](../12-streaming-kappa)).
- Conceitos de ML aplicados a dados: training vs scoring, leakage, point-in-time, drift.

## Estado inicial

Estado final do cap. 12: a plataforma tem sinais históricos (lakehouse), incrementais (CDC) e em tempo real (streaming). Falta consolidá-los numa visão por pagamento.

## Passo 1 — Ambiente e schema (`features/schema.sql`)

Um Postgres com o schema `ml` e a tabela `ml.fraude_pagamento_features`. As colunas já separam claramente: **features** (sinais), **label** (`label_fraude`), **score** (`score_fraude`) e **tempo** (`feature_ts`). A chave é `pagamento_id`.

## Passo 2 — Montar as features (`feature_builder`)

Para cada pagamento, derivar:

- **transacionais** (do OLTP/gold): valor, método, status, quantidade de itens, valor médio do item, cidade do cliente, categoria mais cara;
- **históricas do cliente** (gold, janela relativa ao `feature_ts`): pedidos nos últimos 30 dias, pagamentos recusados nos últimos 30 dias;
- **logísticas** (API externa): ocorrências de entrega;
- **tempo real** (streaming): velocidade média de entrega nos últimos 5 minutos.

## Passo 3 — Point-in-time correctness

Toda feature agregada (ex.: "últimos 30 dias") deve ser calculada **relativa ao `feature_ts`**, não a hoje. Isso garante que o que o modelo vê no treino é exatamente o que estaria disponível no momento da decisão. Implementar com janelas temporais ancoradas no timestamp do pagamento.

## Passo 4 — Evitar label leakage

Nenhuma coluna pode carregar informação que só existe *depois* de conhecer a fraude (ex.: status pós-estorno, decisão manual de analista). Revisar feature por feature: "isso já estava disponível no `feature_ts`?".

## Passo 5 — Equivalência treino/scoring

Garantir que a mesma definição de feature gera o dataset de treino (rotulado, histórico) e o de scoring (novos pagamentos, sem label). Centralizar a lógica num único builder evita divergência entre os dois momentos.

## Validações (definição de pronto)

- [ ] `ml.fraude_pagamento_features` separa feature, label e timestamp.
- [ ] Features agregadas respeitam o `feature_ts` (point-in-time).
- [ ] Nenhuma feature contém informação posterior ao pagamento (sem leakage).
- [ ] Treino e scoring usam a mesma definição de features.

## Estado final (fim da trilha)

Uma base de ML confiável, alimentada pelos sinais batch, incrementais e de streaming da plataforma. A jornada fecha mostrando que a engenharia de dados sustenta produtos analíticos avançados — não apenas dashboards. Volte ao [README raiz](../README.md) para a visão geral.

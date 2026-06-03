# Capítulo 13 — Base de ML para fraude de pagamentos 🟡

> **De onde viemos:** a plataforma já tem batch, API externa, lake/lakehouse, CDC e streaming. Agora o objetivo é preparar uma base analítica confiável para um modelo de detecção de fraude — o capítulo é sobre *engenharia de features*, não sobre o modelo em si.

## Cenário de negócio

A NuvemStore quer detectar pagamentos suspeitos. O modelo não precisa ser complexo no início; o ponto do capítulo é mostrar como preparar dados confiáveis para ML, combinando os sinais que a plataforma já produz:

- dados transacionais de pagamento e pedido (OLTP);
- histórico do cliente no lakehouse;
- ocorrências logísticas da API externa;
- métricas quase em tempo real vindas do streaming.

## O que esta etapa mostra

A montagem de uma **feature table** (`ml.fraude_pagamento_features`, DDL em [`features/schema.sql`](./features/schema.sql)) que reúne, por pagamento, as colunas de feature, a label e o timestamp — pronta para treino e scoring. Não cria fonte nova: consolida o que já existe.

```text
features  -> valor, método, cidade, qtd itens, pedidos do cliente nos últimos 30d,
             pagamentos recusados nos últimos 30d, velocidade média de entrega...
label     -> label_fraude
tempo     -> feature_ts (quando a feature foi calculada)
```

## Conceitos

**Feature table.** Uma tabela onde cada linha é uma unidade a pontuar (um pagamento) e as colunas são os sinais preditivos. Centraliza a definição de feature para treino e scoring usarem exatamente a mesma.

**Training vs scoring dataset.** O treino usa exemplos rotulados do passado; o scoring pontua casos novos sem label. As features precisam ser computáveis em ambos os momentos — features disponíveis só no histórico inviabilizam o scoring.

**Label leakage.** O erro clássico: incluir na feature uma informação que só existe *depois* de saber o resultado (ex.: `status_pagamento` = "estornado por fraude"). O modelo fica ótimo no treino e inútil na produção.

**Point-in-time correctness.** Cada feature deve refletir o que se sabia *no momento do pagamento*, não o estado atual. "Pedidos do cliente nos últimos 30 dias" tem que ser relativo ao `feature_ts`, não a hoje. O `feature_ts` é o que torna isso auditável.

**Batch vs real-time features.** Algumas features vêm de agregações batch (histórico de 30d); outras de streaming (velocidade média 5min). Combiná-las exige cuidado de tempo e disponibilidade.

**Drift.** Em produção, a distribuição das features muda com o tempo. Monitorar drift é o que mantém o modelo confiável depois do deploy.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base / documentação.** O compose sobe um Postgres simples como base de features local (`ml.fraude_pagamento_features`). A construção da feature table a partir das fontes é o roteiro descrito no BUILD; no futuro pode ser materializada no lakehouse ou numa feature store dedicada.

- **[RUNBOOK.md](./RUNBOOK.md)** — subir a base de features e inspecionar o schema.
- **[BUILD.md](./BUILD.md)** — o roteiro: montar as features a partir de gold/CDC/streaming, com point-in-time correctness e sem leakage.

## A dor que sobra

Com a base de ML preparada, a trilha fecha mostrando que a plataforma não serve apenas dashboards — ela sustenta produtos analíticos avançados, com dados confiáveis, históricos e em tempo real.

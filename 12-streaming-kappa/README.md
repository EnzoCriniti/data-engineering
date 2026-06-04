# Capítulo 12 — Streaming em tempo real (Kappa) 🟡

> **De onde viemos:** o [cap. 11](../11-cdc-com-debezium) captura mudanças quase em tempo real, mas só *transporta* eventos. O negócio também precisa *calcular* métricas ao vivo — média móvel, contagem por janela, anomalias — e isso exige processamento contínuo com estado.

## Cenário de negócio

A NuvemStore recebe eventos de GPS dos entregadores. A área de Operações quer acompanhar entregas ativas por região, velocidade média e anomalias, tudo em janelas de tempo e em tempo real. Recalcular isso em batch a cada minuto não entrega a latência necessária.

Essa necessidade pede **processamento de stream com estado**, na arquitetura **Kappa** (um único caminho de stream, sem a camada batch paralela do Lambda).

## O que esta etapa mostra

O núcleo de uma plataforma de streaming:

- **Redpanda** — o log de eventos (tópicos) que recebe o fluxo de GPS.
- **Redpanda Console** — inspeção dos tópicos, partições e mensagens.

Sobre ele se constroem o producer (gera os eventos de GPS), o processor (agrega em janelas) e os sinks (persistem as métricas) — descritos no BUILD.

## Conceitos

**Lambda vs Kappa.** Lambda mantém dois caminhos (batch + streaming) e reconcilia; Kappa usa só o stream como fonte de verdade, reprocessando o log quando precisa de histórico. Kappa é mais simples de operar — uma lógica só.

**Event time vs processing time.** O tempo em que o evento *ocorreu* (event time) difere de quando foi *processado*. Métricas corretas usam event time, porque a rede atrasa e reordena eventos.

**Janelas: tumbling, sliding e session.** Tumbling = janelas fixas e disjuntas; sliding = janelas que se sobrepõem; session = janelas definidas por inatividade. A escolha depende da métrica (ex.: velocidade média nos últimos 5 min = sliding).

**Watermark.** Um limite que diz "não espero mais eventos anteriores a este ponto", permitindo fechar janelas mesmo com eventos atrasados — equilíbrio entre latência e completude.

**Estado, checkpointing e backpressure.** Agregações guardam estado; o checkpointing o persiste para tolerância a falha; backpressure é o mecanismo que evita que um produtor rápido afogue um consumidor lento.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe Redpanda e o Console. O producer, o processor, os tópicos e os sinks são o próximo passo de implementação.

Para subir o ambiente de streaming e acessar o Console, veja o **[RUNBOOK.md](./RUNBOOK.md)**.

## ⚠️ Nota de produção: Para onde vão as métricas do streaming?

O README menciona que "sinks persistem as métricas" — mas **onde** persistir é uma decisão arquitetural crítica que muda tudo.

**Object storage (Delta Lake / S3)** é o sink natural do lakehouse. Mas tem um problema: o Delta Lake tem latência de minutos entre a escrita e a leitura — microbatches que consolidam arquivos Parquet, checkpoint do `_delta_log`, invalidação de cache do Trino. Para um painel que atualiza a cada segundo mostrando entregas ativas por região, isso não serve.

**O padrão correto para métricas operacionais de baixa latência:**

```
Redpanda (eventos de GPS)
        ↓
  Processador de stream (Flink/PySpark Streaming)
        ↓
  ┌─────────────────────────────────────────────┐
  │ Sink 1: Redis / Apache Pinot / Druid        │  ← dashboard operacional (< 1s)
  │ Sink 2: Delta Lake (via microbatch)         │  ← histórico analítico (minutos)
  └─────────────────────────────────────────────┘
```

| Destino | Latência de leitura | Caso de uso | Quando usar |
|---|---|---|---|
| **Redis** (sorted sets) | < 1ms | Rankings, contadores, estado atual | Métricas simples, muitas leituras por segundo |
| **Apache Pinot** | < 100ms | OLAP sobre stream, queries SQL | Dashboards analíticos sobre dados recentes |
| **Apache Druid** | < 100ms | Time-series de alta cardinalidade | Métricas de séries temporais com granularidade fina |
| **Delta Lake** | minutos | Histórico, auditoria, reprocessamento | Análise exploratória, não dashboard |
| **Postgres** | < 10ms | Serving layer com índice | Quando o volume de eventos é gerenciável |

Nesta plataforma, as métricas de GPS (velocidade média, entregas ativas por região) iriam para **Redis** ou **Pinot** para o painel operacional de Operações, e adicionalmente para o **Delta Lake** para alimentar a análise histórica de logística e treino de modelos (cap. 13).

> A escolha do sink é a decisão de design mais importante do streaming — e ela é ditada pela latência de leitura exigida, não pelo volume de dados.

---

## A dor que sobra

Com batch, lakehouse, CDC e streaming, a plataforma tem sinais históricos e recentes. A próxima etapa é preparar esses dados para um caso de ML: fraude de pagamentos. → [Capítulo 13: base de ML para fraude](../13-base-ml-fraude).

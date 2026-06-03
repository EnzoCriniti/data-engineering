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

**Status: 🟡 ambiente base.** O compose sobe Redpanda e o Console. O producer, o processor, os tópicos e os sinks são o roteiro de construção descrito no BUILD.

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o ambiente de streaming e acessar o Console.
- **[BUILD.md](./BUILD.md)** — o roteiro: producer de GPS, processamento por janelas com event time/watermark, e persistência das métricas.

## A dor que sobra

Com batch, lakehouse, CDC e streaming, a plataforma tem sinais históricos e recentes. A próxima etapa é preparar esses dados para um caso de ML: fraude de pagamentos. → [Capítulo 13: base de ML para fraude](../13-base-ml-fraude).

# Build — Capítulo 12: como construir o Streaming Kappa

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Processar eventos contínuos (GPS de entregadores) com janelas e estado, na arquitetura Kappa, calculando métricas ao vivo por região e detectando anomalias — usando o log de eventos como fonte de verdade.

## Pré-requisitos de conhecimento

- O log de eventos do [cap. 11](../11-cdc-com-debezium) (Redpanda/Kafka).
- Event time vs processing time, janelas (tumbling/sliding/session), watermark, estado e checkpointing.

## Estado inicial

Estado final do cap. 11: eventos de mudança fluindo por um log Kafka-compatible. Aqui o log recebe também eventos operacionais (GPS), e passamos a *computar* sobre o fluxo.

## Passo 1 — Ambiente (`docker-compose.yml`)

Redpanda e o Console. Conforme a stack de processamento escolhida (Spark Structured Streaming, Flink ou Kafka Streams), adicionar o serviço correspondente.

## Passo 2 — Tópicos e producer (`producer/gps_producer.py`)

Criar o tópico `gps-entregadores` (particionado por entregador/região para paralelismo). O producer gera eventos com `(entregador_id, regiao, lat, lon, velocidade, event_time)`, simulando o fluxo real.

## Passo 3 — Processor por janelas (`processor/janelas.py`)

Consumir o tópico usando **event time** e definir as janelas conforme a métrica:

- velocidade média por região nos últimos N minutos → janela *sliding*;
- contagem de entregas ativas → janela *tumbling*;
- detecção de anomalia → comparação contra a média da janela.

Definir o **watermark** para tolerar eventos atrasados sem travar o fechamento das janelas. Habilitar **checkpointing** para tolerância a falha do estado.

## Passo 4 — Sinks

Persistir as métricas calculadas no lakehouse (para histórico e auditoria) e, se necessário, num tópico de saída para consumo ao vivo pela operação.

## Passo 5 — Validação por recomputação batch

Reprocessar a mesma janela em batch e comparar os agregados com a saída do streaming. Manter o batch como auditoria/reprocessamento, não como fonte primária de baixa latência (princípio Kappa).

## Validações (definição de pronto)

- [ ] O producer publica eventos de GPS no tópico.
- [ ] O processor calcula métricas por janela usando event time.
- [ ] Watermark fecha janelas corretamente mesmo com eventos atrasados.
- [ ] Agregados streaming batem com a recomputação batch da mesma janela.

## Estado final (gabarito para o próximo capítulo)

Métricas ao vivo calculadas com estado e janelas, persistidas para histórico. Com sinais batch, CDC e streaming disponíveis, a próxima etapa é combiná-los numa base de features para ML. Gancho para o [cap. 13: base de ML para fraude](../13-base-ml-fraude).

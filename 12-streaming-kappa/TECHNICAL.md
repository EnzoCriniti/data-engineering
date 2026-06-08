# Complemento técnico — Streaming, Kappa e processamento com estado

## O que este capítulo aprofunda

Este capítulo passa de transporte de eventos para processamento contínuo. A questão deixa de ser "o que mudou?" e vira "qual métrica está acontecendo agora?".

## Pequena história

Arquiteturas streaming cresceram com logs distribuidos e sistemas como Kafka, Storm, Flink e Spark Streaming. No inicio, era comum usar arquitetura Lambda: um caminho batch para resultados corretos e um caminho streaming para baixa latência.

Kappa surgiu como uma simplificacao: manter apenas o caminho de stream. Para reprocessar, basta reler o log desde o inicio ou desde um offset conhecido. Essa ideia ficou atraente quando logs distribuidos passaram a reter eventos por mais tempo e processadores de stream ficaram mais confiáveis.

## Por baixo dos panos

Stream é uma sequencia sem fim conhecido. Para calcular métricas, o processador precisa recortar o fluxo em janelas.

- Tumbling window: janelas fixas sem sobreposicao.
- Sliding window: janelas que se sobrepoem.
- Session window: janela baseada em atividade e inatividade.

Também existe diferenca entre event time e processing time. Event time é quando o evento aconteceu. Processing time é quando o sistema processou. Em dados reais, eventos atrasam e chegam fora de ordem.

Watermark e o mecanismo que diz até quando o sistema espera eventos atrasados antes de fechar uma janela.

## Estado e checkpoint

Agregações de stream precisam manter estado. Para calcular entregas ativas por regiao nos ultimos 5 minutos, o processador guarda contagens parciais por chave e janela.

Checkpoint salva esse estado periodicamente. Se o processo cai, ele volta de um checkpoint e contínua sem recomecar do zero.

Backpressure acontece quando produtores geram eventos mais rapido que consumidores processam. Sistemas maduros precisam controlar essa pressao, escalar consumidores ou acumular lag sem cair.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Apache Flink | Muito forte em event time, estado e baixa latência. |
| Spark Structured Streaming | Bom quando o ecossistema já usa Spark e lakehouse. |
| Kafka Streams | Biblioteca Java integrada ao Kafka. |
| Materialize | Banco streaming para views materializadas incrementais. |
| RisingWave | Banco streaming SQL moderno. |

## Quando usar

Use streaming quando a decisão precisa acontecer em segundos ou minutos: fraude, operação, alertas, IoT, rastreamento e monitoramento.

Evite streaming quando um batch de hora em hora resolve. Streaming aumenta complexidade: estado, atraso, ordenacao, reprocessamento e operação contínua.

## Como isso aparece no projeto

O capítulo 12 usa eventos de GPS para demonstrar métricas ao vivo. A arquitetura Kappa mostra que o mesmo log pode alimentar tempo real, reprocessamento histórico e features recentes para casos de ML
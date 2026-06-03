# Capítulo 11 — CDC com Debezium 🟡

> **De onde viemos:** o [cap. 10](../10-lakehouse-medallion) deu confiabilidade ao lake, mas ainda trabalha em batch. Para alguns casos — risco e fraude — dado de horas atrás não serve. Precisamos capturar as mudanças do banco continuamente.

## Cenário de negócio

A NuvemStore precisa acompanhar mudanças de pagamentos quase em tempo real para alimentar a análise de risco e fraude. Recarregar tabelas inteiras a cada minuto é caro e pesa na origem — além de só enxergar o estado final, perdendo o histórico de cada mudança.

O **CDC (Change Data Capture)** resolve isso lendo o log de transações do próprio banco: cada insert, update e delete vira um evento, sem consultar as tabelas.

## O que esta etapa mostra

A captura de mudanças do Postgres via log, transportada por um log Kafka-compatible:

- **Postgres** com `wal_level=logical` — expõe o log de transações para replicação lógica.
- **Redpanda** — log de eventos compatível com Kafka, destino dos eventos de mudança.
- **Kafka Connect + Debezium** — o conector que lê o WAL e publica os eventos.
- **Redpanda Console** — inspeção dos tópicos e mensagens.

## Conceitos

**CDC vs polling batch.** Polling consulta a tabela periodicamente e só vê o estado atual; o CDC lê o log e captura *cada* mudança, com baixíssimo impacto na origem. É a diferença entre fotografar de hora em hora e filmar.

**WAL e replicação lógica.** O Write-Ahead Log do Postgres registra toda alteração antes de aplicá-la. Com `wal_level=logical`, o Debezium se inscreve nesse log e decodifica as mudanças como eventos estruturados.

**Snapshot inicial + streaming.** O conector primeiro tira um snapshot do estado atual das tabelas e, em seguida, passa a transmitir as mudanças incrementais. Isso garante que o destino comece consistente e siga atualizado.

**At-least-once e idempotência no sink.** O Kafka Connect entrega *pelo menos uma vez* — eventos podem repetir. Por isso o sink aplica as mudanças de forma idempotente (`MERGE` por chave), tornando reprocessamento seguro.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe Postgres (logical), Redpanda, Kafka Connect/Debezium e o Console. O conector Debezium (JSON) e o sink para o lakehouse são o roteiro de construção descrito no BUILD.

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o ambiente CDC e acessar Connect/Console.
- **[BUILD.md](./BUILD.md)** — o roteiro: configurar o conector, snapshot + streaming, e o sink idempotente no lakehouse.

## A dor que sobra

O CDC transporta mudanças, mas não calcula métricas com janelas e estado (média móvel, contagem por janela). → [Capítulo 12: Streaming Kappa](../12-streaming-kappa).

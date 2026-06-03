# Build — Capítulo 11: como construir o CDC com Debezium

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Capturar mudanças do Postgres OLTP via log de transações (WAL) com Debezium, publicá-las num log Kafka-compatible (Redpanda) e aplicá-las no lakehouse de forma idempotente — substituindo recargas batch completas por cargas incrementais baseadas em evento.

## Pré-requisitos de conhecimento

- O OLTP da trilha ([cap. 00](../00-modelagem-transacional)) e o lakehouse ([cap. 10](../10-lakehouse-medallion)).
- WAL e replicação lógica do Postgres, Kafka Connect, semântica at-least-once, `MERGE`.

## Estado inicial

Estado final do cap. 10: lakehouse confiável, porém batch. A origem das mudanças é o Postgres OLTP, que precisa estar com `wal_level=logical`.

## Passo 1 — Ambiente (`docker-compose.yml`)

Postgres com `wal_level=logical` (e `max_replication_slots`/`max_wal_senders` adequados), Redpanda, Kafka Connect com a imagem Debezium e o Redpanda Console.

## Passo 2 — Configurar o conector Debezium (`config/debezium-postgres.json`)

JSON do conector apontando para o Postgres, listando as tabelas relevantes (ex.: `public.pagamento`, `public.pedido`), com `plugin.name=pgoutput`, `snapshot.mode` apropriado e o mapeamento de tópicos. Registrar via `POST /connectors`.

## Passo 3 — Snapshot inicial + streaming

1. tirar o snapshot inicial das tabelas relevantes;
2. comparar o snapshot com a camada silver/gold atual (reconciliação de ponto de partida);
3. deixar o conector transmitir as mudanças do WAL continuamente.

## Passo 4 — Sink idempotente para o lakehouse

Consumir os tópicos de mudança e aplicar no lakehouse com `MERGE` por chave natural, tratando os três tipos de operação (`c`=insert, `u`=update, `d`=delete). Como a entrega é at-least-once, o `MERGE` garante que reprocessar um evento não duplique nem corrompa.

## Passo 5 — Migrar de batch para incremental

Uma vez validado o fluxo, reduzir as cargas batch completas dessas tabelas para cargas incrementais baseadas em evento.

## Validações (definição de pronto)

- [ ] O conector aparece em `RUNNING` no `/status`.
- [ ] Insert/update/delete na origem produzem eventos nos tópicos.
- [ ] O sink reflete as três operações no lakehouse.
- [ ] Reprocessar eventos (at-least-once) não duplica linhas no destino.

## Estado final (gabarito para o próximo capítulo)

Mudanças do OLTP fluindo continuamente para o lakehouse, sem recarga total. Falta calcular métricas com janelas e estado sobre fluxos — gancho para o [cap. 12: Streaming Kappa](../12-streaming-kappa).

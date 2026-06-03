# Gabarito de estado - Capitulo 11

## Objetivo do capitulo

Atualizar a plataforma analitica quase em tempo real usando CDC com Debezium.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 10:

- OLTP populado;
- lakehouse com bronze, silver e gold;
- metricas batch funcionando;
- necessidade de reduzir latencia de atualizacao.

## Etapas do capitulo

1. Subir Postgres com logical replication.
2. Subir Redpanda.
3. Subir Kafka Connect com Debezium.
4. Registrar conector para tabelas relevantes.
5. Executar snapshot inicial.
6. Capturar inserts, updates e deletes pelo WAL.
7. Aplicar eventos no destino com operacao idempotente.

## Estado final esperado

Ao final, deve existir:

- topicos CDC por tabela ou dominio;
- snapshot inicial publicado;
- eventos de mudanca chegando no log;
- sink aplicando mudancas no lakehouse;
- camada analitica atualizada sem recarga completa.

## Validacoes

- Kafka Connect mostra conector ativo.
- Topicos recebem eventos.
- Um update no Postgres gera evento CDC.
- Um delete no Postgres gera evento CDC.
- O destino absorve duplicatas sem duplicar linhas.
- Contagem apos snapshot bate com a origem.

## Como o proximo capitulo usa este estado

O capitulo 12 parte do log de eventos e adiciona processamento de stream com estado e janelas de tempo.

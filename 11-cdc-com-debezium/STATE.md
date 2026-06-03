# Gabarito de estado - Capítulo 11

## Objetivo do capítulo

Atualizar a plataforma analítica quase em tempo real usando CDC com Debezium.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 10:

- OLTP populado;
- lakehouse com bronze, silver e gold;
- métricas batch funcionando;
- necessidade de reduzir latência de atualizacao.

## Etapas do capítulo

1. Subir Postgres com logical replication.
2. Subir Redpanda.
3. Subir Kafka Connect com Debezium.
4. Registrar conector para tabelas relevantes.
5. Executar snapshot inicial.
6. Capturar inserts, updates e deletes pelo WAL.
7. Aplicar eventos no destino com operação idempotente.

## Estado final esperado

Ao final, deve existir:

- topicos CDC por tabela ou domínio;
- snapshot inicial publicado;
- eventos de mudança chegando no log;
- sink aplicando mudanças no lakehouse;
- camada analítica atualizada sem recarga completa.

## Validações

- Kafka Connect mostra conector ativo.
- Topicos recebem eventos.
- Um update no Postgres gera evento CDC.
- Um delete no Postgres gera evento CDC.
- O destino absorve duplicatas sem duplicar linhas.
- Contagem após snapshot bate com a origem.

## Como o proximo capítulo usa este estado

O capítulo 12 parte do log de eventos e adiciona processamento de stream com estado e janelas de tempo.

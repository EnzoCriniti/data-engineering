# Complemento tecnico - CDC, Debezium, Kafka Connect e Redpanda

## O que este capitulo aprofunda

Este capitulo trata de mudancas em tempo quase real. Em vez de recarregar tabelas inteiras, o pipeline escuta o log de transacoes da origem e publica eventos de `INSERT`, `UPDATE` e `DELETE`.

## Pequena historia

CDC existe ha muito tempo em bancos corporativos e replicacao. O que mudou foi a popularizacao de logs distribuidos como Kafka e conectores open source.

Kafka nasceu no LinkedIn no inicio da decada de 2010 para lidar com alto volume de eventos. Depois virou projeto Apache e se tornou uma das bases de arquiteturas event-driven.

Debezium surgiu na segunda metade da decada de 2010 como uma forma open source de fazer CDC a partir de bancos como PostgreSQL, MySQL, SQL Server e outros, normalmente usando Kafka Connect.

Redpanda apareceu depois como uma alternativa Kafka-compatible, escrita em C++, com foco em simplicidade operacional e baixa latencia.

## Por baixo dos panos do CDC

Bancos transacionais registram alteracoes em logs internos para garantir durabilidade e recuperacao. No PostgreSQL, o WAL registra mudancas antes que elas sejam consideradas persistidas.

Com logical replication, o Postgres expoe mudancas em formato consumivel. Debezium atua como uma replica logica: le o WAL, controla offset e transforma mudancas em eventos.

Normalmente o fluxo tem duas fases:

1. Snapshot inicial: copia o estado atual da tabela.
2. Streaming: publica apenas mudancas novas.

Cada evento carrega chave, estado anterior, estado novo, operacao e metadados. O consumidor precisa entender deletes, updates e duplicidade eventual.

## Kafka Connect

Kafka Connect e um framework para rodar conectores. Ele gerencia configuracao, offsets, tarefas e tolerancia a falhas.

O Debezium e o conector de source. Ele publica eventos em topicos. Um sink posterior pode gravar em Delta, Postgres, Elasticsearch, S3 ou outro destino.

## Garantias e idempotencia

Muitos pipelines de eventos trabalham com entrega at-least-once. Isso significa que uma mensagem pode ser entregue mais de uma vez.

Por isso o destino precisa ser idempotente. Em lakehouse, o padrao e usar `MERGE` por chave primaria e versao/ordem do evento. Assim duplicatas nao viram linhas duplicadas.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| AWS DMS | Servico gerenciado de migracao e CDC. |
| Oracle GoldenGate | Solucao enterprise tradicional para replicacao. |
| Striim | Plataforma comercial para streaming e CDC. |
| Maxwell's Daemon | CDC para MySQL, mais especifico. |
| Estuary / Airbyte CDC | Conectores modernos com foco em integracao de dados. |

## Quando usar

Use CDC quando precisa de baixa latencia e nao quer sobrecarregar a origem com polling frequente.

Evite CDC quando a origem nao tem log confiavel, quando a ordem de eventos nao pode ser tratada ou quando um batch simples atende o SLA.

## Como isso aparece no projeto

O capitulo 11 conecta a origem transacional ao mundo de eventos. O lakehouse do capitulo 10 vira destino natural, porque suporta `MERGE` e historico para absorver mudancas.

# Capitulo 11 - CDC com Debezium

> De onde viemos: o lakehouse melhora confiabilidade, mas ainda trabalha em batch. Para alguns casos, dado de horas atras nao serve.

## Cenario de negocio

A NuvemStore precisa acompanhar mudancas de pagamentos quase em tempo real para alimentar analise de risco e fraude. Recarregar tabelas inteiras a cada minuto e caro e pesa na origem.

CDC resolve essa dor lendo o log de transacoes do banco.

## Status desta etapa

Status atual: **ambiente base**.

O compose sobe:

- Postgres com `wal_level=logical`;
- Redpanda como log Kafka-compatible;
- Kafka Connect com imagem Debezium;
- Redpanda Console.

O conector Debezium em JSON e o sink para lakehouse serao implementados depois.

## Como esta etapa migra a anterior

CDC entra para manter o lakehouse atualizado sem recarregar tudo. Ele deve partir do OLTP real da trilha e atualizar a camada analitica ja existente.

Plano de migracao:

1. tirar snapshot inicial das tabelas relevantes do Postgres;
2. comparar o snapshot com a camada silver/gold atual;
3. registrar o conector Debezium para capturar mudancas pelo WAL;
4. aplicar eventos no destino com operacao idempotente, como `MERGE`;
5. validar que inserts, updates e deletes aparecem no lakehouse;
6. reduzir cargas batch completas para cargas incrementais baseadas em evento.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

Kafka Connect:

```text
http://localhost:8083
```

Redpanda Console:

```text
http://localhost:8080
```

## Conceitos principais

- CDC vs polling batch.
- WAL e logical replication.
- Snapshot inicial + streaming.
- Kafka Connect e gerenciamento de offsets.
- Entrega at-least-once e idempotencia no sink.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## A dor que sobra

CDC transporta mudancas, mas nao calcula metricas com janelas e estado. Essa dor leva ao capitulo 12: Streaming Kappa.

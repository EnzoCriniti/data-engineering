# Runbook — Capítulo 11: CDC com Debezium

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — Postgres (logical), Redpanda, Kafka Connect/Debezium e Console sobem prontos; o conector e o sink ainda serão implementados (ver [BUILD.md](./BUILD.md)).

## O que este capítulo entrega hoje

O ambiente de CDC: Postgres com `wal_level=logical`, Redpanda como log Kafka-compatible, Kafka Connect com a imagem Debezium e o Redpanda Console para inspeção.

## Pré-requisitos

- Docker e Docker Compose.
- Portas livres: `8083` (Kafka Connect) e `8080` (Redpanda Console).

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

UIs:

```text
Kafka Connect:    http://localhost:8083
Redpanda Console: http://localhost:8080
```

## Conferir

```bash
# Connect no ar e plugins disponíveis (deve listar o Debezium Postgres)
curl http://localhost:8083/connector-plugins

# conectores registrados (vazio até criar o conector)
curl http://localhost:8083/connectors
```

## Quando o conector estiver implementado

```bash
# registrar o conector Debezium (JSON do conector em config/)
curl -X POST -H "Content-Type: application/json" \
  --data @config/debezium-postgres.json \
  http://localhost:8083/connectors

# status do conector
curl http://localhost:8083/connectors/nuvemstore-cdc/status
```

**Validação:** inserts, updates e deletes na origem devem aparecer como eventos nos tópicos (visíveis no Console) e, depois, refletir no lakehouse via sink idempotente.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 12](../12-streaming-kappa): processar esses eventos com janelas e estado para métricas ao vivo.

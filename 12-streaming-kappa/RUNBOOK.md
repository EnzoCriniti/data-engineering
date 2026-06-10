# Runbook — Capítulo 12: Streaming Kappa

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — Redpanda e o Console sobem prontos; producer, processor e sinks ainda serão implementados (ver [GUIDE.md](./GUIDE.md) para o passo-a-passo e [SOLUTION.md](./SOLUTION.md) para o código).

## O que este capítulo entrega hoje

O log de eventos para streaming: Redpanda (Kafka-compatible) e o Redpanda Console para inspecionar tópicos, partições e mensagens.

## Pré-requisitos

- Docker e Docker Compose.
- Porta `8080` livre (Redpanda Console).

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

UI:

```text
Redpanda Console: http://localhost:8080
```

## Conferir

```bash
# listar tópicos (via rpk dentro do container)
docker compose exec redpanda rpk topic list

# criar um tópico de teste
docker compose exec redpanda rpk topic create gps-entregadores
```

## Quando os jobs estiverem implementados

```bash
# producer de eventos de GPS
docker compose exec redpanda rpk topic create gps-entregadores
python simulators/gps_producer.py
# processor de janelas (event time + watermark)
docker compose run spark-submit spark-submit /app/jobs/streaming_gps.py
```

**Validação:** os agregados do streaming (ex.: velocidade média por janela) devem bater com uma recomputação batch da mesma janela; o batch fica como auditoria/reprocessamento, não como fonte de baixa latência.

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 13](../13-base-ml-fraude): preparar uma base de features combinando os sinais batch, CDC e streaming para um modelo de fraude.

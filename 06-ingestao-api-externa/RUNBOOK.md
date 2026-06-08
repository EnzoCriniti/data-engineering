# Runbook — Capítulo 06: ingestão batch de API externa

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — o extractor ainda será implementado (ver [GUIDE.md](./GUIDE.md) para o passo-a-passo e [SOLUTION.md](./SOLUTION.md) para o código).

## O que este capítulo entrega hoje

Uma API fake da transportadora e um Postgres de warehouse com schema `staging`, prontos para receber o extractor.

## Pré-requisitos

- Docker e Docker Compose.
- Porta `8000` livre para a API fake.

## Subir o ambiente base

```bash
cp .env.example .env
docker compose up -d
```

## Consultar a API fake

```bash
curl http://localhost:8000/entregas.json
```

Você verá o payload de entregas (status, previsão, ocorrências, `atualizado_em`) que o extractor vai consumir.

## Quando o extractor estiver implementado

```bash
docker compose run --rm extractor    # extrai a janela incremental e carrega staging
docker compose exec warehouse psql -U analytics -d warehouse -c \
  "SELECT COUNT(*), COUNT(DISTINCT entrega_id) FROM staging.transportadora_entregas;"
```

**Validação:** as duas contagens devem ser iguais (sem duplicatas por `entrega_id`).

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 07](../07-orquestracao-com-airflow): orquestrar OLTP, API externa e dbt com Airflow.

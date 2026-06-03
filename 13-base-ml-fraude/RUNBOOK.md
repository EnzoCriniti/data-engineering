# Runbook — Capítulo 13: base de ML para fraude

> Guia rápido para **subir e usar**. Status atual: **ambiente base / documentação** — o Postgres de features sobe pronto com o schema `ml`; a carga das features a partir das fontes é o roteiro do [BUILD.md](./BUILD.md).

## O que este capítulo entrega hoje

Um Postgres com o schema `ml` e a tabela `ml.fraude_pagamento_features` criada (vazia), com as colunas de feature, a label (`label_fraude`) e o timestamp (`feature_ts`) já modeladas.

## Pré-requisitos

- Docker e Docker Compose.
- Porta do Postgres livre (confira no `.env.example`).

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

## Conferir o schema

```bash
docker compose exec db psql -U app -d nuvemstore -c "\d ml.fraude_pagamento_features"
```

Você verá as colunas de feature (valor, método, cidade, contagens dos últimos 30 dias, velocidade média de entrega), a `label_fraude`, o `score_fraude` e o `feature_ts`.

## Quando a carga estiver implementada

```bash
# job que monta a feature table a partir de gold/CDC/streaming
docker compose run --rm feature_builder
# inspecionar
docker compose exec db psql -U app -d nuvemstore -c \
  "SELECT count(*), count(label_fraude) FROM ml.fraude_pagamento_features;"
```

**Validação:** treino e scoring devem usar a mesma definição de feature; nenhuma coluna pode conter informação posterior ao `feature_ts` (sem label leakage).

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Fim da trilha

Este é o último capítulo. A plataforma cobre da modelagem transacional à base de ML — voltando ao [README raiz](../README.md) para a visão geral da jornada.

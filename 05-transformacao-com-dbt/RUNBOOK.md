# Runbook — Capítulo 05: transformação com dbt

> Guia rápido para **subir e usar** o ambiente. Status atual: **ambiente base** — o projeto dbt ainda será implementado (ver [BUILD.md](./BUILD.md)). Os comandos de `dbt` abaixo ficam prontos para quando os modelos existirem.

## O que este capítulo entrega hoje

O ambiente base com a camada de BI (Metabase) pronta para consumir os marts quando o projeto dbt for materializado.

## Pré-requisitos

- Docker e Docker Compose.
- Porta `3002` livre para o Metabase.

## Subir o ambiente base

```bash
cp .env.example .env
docker compose up -d
```

UI do Metabase: `http://localhost:3002`.

## Quando o projeto dbt estiver implementado

Os comandos padrão de operação serão:

```bash
dbt deps          # instala pacotes
dbt build         # roda modelos + testes (staging -> marts)
dbt docs generate # gera documentação e lineage
dbt docs serve    # navega o grafo de dependências
```

**Validação esperada:** as contagens e métricas dos marts dbt devem bater com os marts manuais do capítulo 04 (`mart_receita_diaria`, `mart_top_produtos`).

## Recomeçar do zero

```bash
docker compose down -v
docker compose up -d
```

## Próximo passo

[Capítulo 06](../06-ingestao-api-externa): adicionar uma fonte externa batch (transportadora).

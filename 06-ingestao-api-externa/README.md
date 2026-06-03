# Capitulo 06 - Ingestao batch de API externa

> De onde viemos: dbt organizou as transformacoes, mas a plataforma ainda depende basicamente do OLTP interno. Na vida real, logo aparecem fontes externas.

## Cenario de negocio

A NuvemStore terceiriza parte das entregas para a Transportadora X. A transportadora expoe uma API simples com status de entrega, previsao, ocorrencias e timestamp de atualizacao.

Essa fonte nao pertence ao OLTP interno, mas precisa entrar no analytics para medir SLA, atraso e qualidade logistica.

## Status desta etapa

Status atual: **ambiente base/documentacao**.

O compose sobe:

- uma API fake simples da transportadora;
- um Postgres de warehouse com schema `staging`.

O extractor batch Python, paginacao, controle incremental e idempotencia serao implementados depois.

## Como esta etapa migra a anterior

Esta etapa nao substitui o dbt. Ela adiciona uma nova fonte batch que depois sera transformada junto com os dados internos.

Plano de migracao:

1. manter os marts internos do capitulo 05;
2. subir API externa simulando a transportadora;
3. extrair entregas por janela de `atualizado_em`;
4. carregar dados em `staging.transportadora_entregas`;
5. validar duplicidade por `entrega_id`;
6. preparar dbt para cruzar pedido interno com status externo.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

API fake:

```text
http://localhost:8088/entregas.json
```

## Conceitos principais

- Fonte externa batch.
- Contrato de API.
- Janela incremental por `updated_at`.
- Idempotencia por chave natural.
- Staging antes de transformacao.
- Retry e rate limit como dores para o Airflow.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## A dor que sobra

Agora a plataforma tem OLTP interno, dbt e API externa batch. Rodar tudo manualmente fica fragil. Essa dor leva ao capitulo 07: Airflow.

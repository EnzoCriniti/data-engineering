# Capítulo 06 — Ingestão batch de API externa

> **De onde viemos:** o dbt organizou as transformações, mas a plataforma ainda depende basicamente do OLTP interno. Na vida real, logo aparecem fontes externas.

## Cenário de negócio

A NuvemStore terceiriza parte das entregas para a Transportadora X, que expõe uma API simples com status de entrega, previsão, ocorrências e timestamp de atualização. Essa fonte não pertence ao OLTP interno, mas precisa entrar no analytics para medir SLA, atraso e qualidade logística.

## Por que esta stack

| Tecnologia | Por que entra | O que fica de fora |
| --- | --- | --- |
| API HTTP (fake) | Simula a fonte externa da transportadora. | — |
| Postgres (staging) | Aterrissa o dado externo antes de transformar. | — |
| Extractor Python | Extração incremental por janela de tempo. | Airflow — orquestração só no cap. 07. |

## Status desta etapa

**Ambiente base.** O compose sobe uma API fake da transportadora e um Postgres de warehouse com schema `staging`. O extractor batch (paginação, controle incremental, idempotência) é o próximo passo de implementação.

## Conceitos

**Fonte externa vs interna.** Diferente do OLTP, uma API externa não é controlada por você: pode mudar contrato, paginar, ter rate limit, cair, devolver duplicatas. Tratar isso é parte do trabalho.

**Janela incremental por `updated_at`.** Em vez de baixar tudo a cada execução, extrai-se apenas o que mudou desde o último checkpoint (`atualizado_em`). Reduz custo e tempo, mas exige guardar o checkpoint.

**Idempotência por chave natural.** Como a API pode reentregar registros, a carga deduplica por `entrega_id` (upsert). Reexecutar a mesma janela não duplica.

**Staging antes de transformar.** O dado externo aterrissa cru em `staging.transportadora_entregas`; só depois o dbt cruza com o pedido interno. Isola "trazer" de "dar sentido".

> Aprofundamento técnico (contratos de API, retry/backoff, paginação) em [`TECHNICAL.md`](./TECHNICAL.md).

## Como executar

Este README descreve o *porquê*. Para subir o ambiente base e consultar a API fake — comandos, saída esperada e validações — veja o **[RUNBOOK.md](./RUNBOOK.md)**.

## A dor que sobra

Agora a plataforma tem OLTP interno, dbt e uma API externa batch. Rodar tudo manualmente, na ordem certa, com retries, fica frágil. Essa dor leva ao [capítulo 07](../07-orquestracao-com-airflow): orquestração com Airflow.

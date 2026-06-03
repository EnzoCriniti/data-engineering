# Runbook — Capítulo 01: modelagem dimensional

> Guia rápido. Este capítulo é **de modelagem**: não há ambiente próprio para subir. O star schema desenhado aqui é materializado nos capítulos seguintes.

## O que este capítulo entrega

O desenho do modelo dimensional (star schema) da NuvemStore: fato `fct_vendas` e dimensões `dim_tempo`, `dim_cliente` (SCD2), `dim_produto`, `dim_loja`. É um capítulo conceitual — o "alvo" que os pipelines vão materializar.

## Como ver o modelo funcionando

O star schema vira tabelas reais a partir dos próximos capítulos:

- **[Capítulo 02](../02-dimensional-no-oltp)** — materializa o dimensional no mesmo Postgres (schema `analytics`).
- **[Capítulo 03](../03-warehouse-dedicado)** — materializa num warehouse Postgres dedicado, com o job `migrate` resolvendo surrogate keys.

Siga o RUNBOOK desses capítulos para subir, popular e consultar.

## O diagrama

```bash
cd diagrams
pip install -r requirements.txt   # requer graphviz no sistema
python architecture.py            # gera architecture.png
```

## Próximo passo

[Capítulo 02](../02-dimensional-no-oltp): a primeira materialização do star schema, ainda dentro do OLTP.

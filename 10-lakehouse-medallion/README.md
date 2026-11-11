# 10 — Funil de navegação no lakehouse

## De onde viemos

O capítulo 09 verificou no MinIO os eventos e os pedidos de referência que estavam no HDFS.

## O problema

Produto quer saber onde as sessões abandonam a compra. O resultado precisa ser reproduzível quando um evento chega tarde e o relatório é recalculado.

## Arquitetura

Bronze conserva o histórico em Parquet por lote aprovado. Silver Delta valida, deduplica e vincula compras a pedidos pagos. Gold Delta publica a coorte diária com alcance, perdas e IDs de pedido convertidos. O job Spark local lê e grava sob demanda.

## Conceitos

O `_delta_log` versiona a tabela. Uma versão anterior pode ser lida para conferir o relatório que Produto viu antes do lote tardio. Os manifestos identificam os lotes que entraram em cada versão.

## A dor que sobra

O funil é calculado em lote para uma coorte sintética. A operação tem necessidades diferentes quando a decisão depende de eventos que acabam de ocorrer. [Reproduzir a demonstração](./RUNBOOK.md)

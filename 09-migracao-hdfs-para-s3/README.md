# 09 — Migração do HDFS para MinIO

## De onde viemos

O capítulo 08 conserva eventos de navegação e pedidos de referência em um snapshot Parquet no HDFS.

## O problema

Produto precisa conservar o histórico em object storage e continuar vendo os mesmos resultados de conversão. Totais de linhas iguais podem esconder alterações no conteúdo.

## Arquitetura

Spark lê o HDFS, copia o snapshot para um prefixo candidato no MinIO e relê os dois lados. O manifesto do lote é escrito após a comparação de dados e do funil. A origem segue disponível durante a validação.

## Conceitos

S3A dá acesso ao object storage a partir do Spark. O manifesto funciona como registro de lotes prontos para consumo. `EXCEPT ALL` verifica conteúdo e multiplicidade, incluindo duplicatas.

## A dor que sobra

Os objetos armazenam o histórico validado. O capítulo 10 acrescenta versões transacionais para reconstruir e comparar as métricas. [Executar o capítulo](./RUNBOOK.md)

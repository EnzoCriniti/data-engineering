# 08 — Histórico de navegação no HDFS

## De onde viemos

A fase anterior cruza pedidos do PostgreSQL com entregas da transportadora. Produto agora quer entender em que ponto da compra as sessões param.

## O problema

Cliques, carrinhos e confirmações chegam como JSON. O histórico precisa continuar disponível quando uma regra de validação ou a janela do funil mudar.

## Arquitetura

A fonte sintética emite NDJSON com IDs estáveis. Um job Spark local grava um snapshot em HDFS. Os envelopes Parquet guardam o JSON original e a partição de data UTC. As referências de pedido formam um snapshot à parte dentro do mesmo lote.

## Conceitos

NameNode e DataNode separam metadados e blocos. Particionar Parquet permite ler dias específicos. O hash do conteúdo identifica o snapshot mesmo que os arquivos Parquet sejam regravados.

## A dor que sobra

Operar HDFS só para conservar o histórico mantém armazenamento preso ao ambiente de estudo. O capítulo 09 move o snapshot para MinIO e verifica se o funil continua igual. [Executar o capítulo](./RUNBOOK.md)

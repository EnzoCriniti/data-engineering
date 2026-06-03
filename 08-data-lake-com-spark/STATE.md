# Gabarito de estado - Capitulo 08

## Objetivo do capitulo

Introduzir data lake para dados volumosos e semi-estruturados, usando HDFS on-prem e Spark.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 07:

- pipeline orquestrado;
- dados analiticos existentes;
- warehouse ainda usado para marts;
- necessidade de armazenar historico/eventos fora do warehouse.

## Etapas do capitulo

1. Subir HDFS como zona raw do lake.
2. Subir Spark master e worker.
3. Subir metastore/catalogo para registrar datasets.
4. Gerar ou reaproveitar eventos semi-estruturados.
5. Carregar dados crus no HDFS.
6. Processar dados com Spark.
7. Escrever dados curados em Parquet.
8. Registrar datasets/tabelas no metastore.

## Estado final esperado

Ao final, deve existir:

- zona raw no HDFS;
- arquivos crus;
- dados curados em Parquet;
- tabelas/datasets registrados no metastore;
- jobs Spark versionados;
- warehouse ainda preservado para marts existentes.

## Validacoes

- Arquivos crus existem no HDFS.
- Spark le os dados crus sem erro.
- Saida Parquet e gerada.
- Dataset curado aparece no metastore.
- Contagens do curado batem com a entrada esperada.
- O warehouse nao precisa carregar todo o historico semi-estruturado.

## Como o proximo capitulo usa este estado

O capitulo 09 usa o lake HDFS como legado inicial e simula a migracao gradual para S3/MinIO.

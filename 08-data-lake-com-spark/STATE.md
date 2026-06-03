# Gabarito de estado - Capítulo 08

## Objetivo do capítulo

Introduzir data lake para dados volumosos e semi-estruturados, usando HDFS on-prem e Spark.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 07:

- pipeline orquestrado;
- dados analíticos existentes;
- warehouse ainda usado para marts;
- necessidade de armazenar histórico/eventos fora do warehouse.

## Etapas do capítulo

1. Subir HDFS como zona raw do lake.
2. Subir Spark master e worker.
3. Subir metastore/catálogo para registrar datasets.
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

## Validações

- Arquivos crus existem no HDFS.
- Spark le os dados crus sem erro.
- Saída Parquet e gerada.
- Dataset curado aparece no metastore.
- Contagens do curado batem com a entrada esperada.
- O warehouse não precisa carregar todo o histórico semi-estruturado.

## Como o proximo capítulo usa este estado

O capítulo 09 usa o lake HDFS como legado inicial e simula a migracao gradual para S3/MinIO.

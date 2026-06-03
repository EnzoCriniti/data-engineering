# Gabarito de estado - Capitulo 09

## Objetivo do capitulo

Simular a migracao gradual de um legado HDFS/on-prem para S3/MinIO, mantendo consulta federada durante a transicao.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 08 e adicionar um destino S3/MinIO simulado:

- lakehouse com historico;
- metricas batch e/ou streaming persistidas;
- base de features de fraude;
- historico legado em HDFS;
- diferenca clara entre dados ainda presos ao legado e dados ja migrados para S3.

## Etapas do capitulo

1. Subir HDFS como legado on-prem.
2. Subir MinIO/S3 como alvo moderno da migracao.
3. Subir Spark para mover e consultar dados.
4. Inventariar particoes no HDFS.
5. Migrar historico frio para S3/MinIO.
6. Manter temporariamente particoes quentes ou jobs sensiveis em HDFS.
7. Configurar query engine para federar HDFS e S3.

## Estado final esperado

Ao final, deve existir:

- legado HDFS simulado;
- zona S3/MinIO com historico migrado;
- job de migracao/tiering;
- query federada lendo as duas zonas;
- BI ou consulta SQL sem precisar saber onde cada particao esta.

## Validacoes

- Contagem por particao bate antes e depois da migracao.
- Dados migrados aparecem em S3/MinIO.
- Particoes ainda nao migradas continuam acessiveis via HDFS.
- Query federada retorna o mesmo resultado da consulta completa anterior.
- Politica de migracao/tiering e documentada e reexecutavel.

## Como a trilha fecha este estado

Este estado final mostra uma plataforma que saiu de um lake HDFS on-prem e iniciou a migracao para object storage, preparando o terreno para o lakehouse.

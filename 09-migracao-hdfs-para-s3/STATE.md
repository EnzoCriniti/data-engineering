# Gabarito de estado - Capítulo 09

## Objetivo do capítulo

Simular a migracao gradual de um legado HDFS/on-prem para S3/MinIO, mantendo consulta federada durante a transição.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 08 e adicionar um destino S3/MinIO simulado:

- lakehouse com histórico;
- métricas batch e/ou streaming persistidas;
- base de features de fraude;
- histórico legado em HDFS;
- diferenca clara entre dados ainda presos ao legado e dados já migrados para S3.

## Etapas do capítulo

1. Subir HDFS como legado on-prem.
2. Subir MinIO/S3 como alvo moderno da migracao.
3. Subir Spark para mover e consultar dados.
4. Inventariar partições no HDFS.
5. Migrar histórico frio para S3/MinIO.
6. Manter temporariamente partições quentes ou jobs sensiveis em HDFS.
7. Configurar query engine para federar HDFS e S3.

## Estado final esperado

Ao final, deve existir:

- legado HDFS simulado;
- zona S3/MinIO com histórico migrado;
- job de migracao/tiering;
- query federada lendo as duas zonas;
- BI ou consulta SQL sem precisar saber onde cada partição está.

## Validações

- Contagem por partição bate antes e depois da migracao.
- Dados migrados aparecem em S3/MinIO.
- Partições ainda não migradas continuam acessiveis via HDFS.
- Query federada retorna o mesmo resultado da consulta completa anterior.
- Politica de migracao/tiering e documentada e reexecutável.

## Como a trilha fecha este estado

Este estado final mostra uma plataforma que saiu de um lake HDFS on-prem e iniciou a migracao para object storage, preparando o terreno para o lakehouse.

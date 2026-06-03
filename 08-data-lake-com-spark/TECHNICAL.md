# Complemento tecnico - Spark, HDFS, Metastore e Parquet

## O que este capitulo aprofunda

Este capitulo sai do warehouse pequeno e entra em dados semi-estruturados em escala. A primeira solucao da empresa e aproveitar infraestrutura on-prem existente com HDFS e processamento distribuido com Spark.

## Pequena historia

Apache Spark nasceu no AMPLab da UC Berkeley no fim da decada de 2000 e ganhou muita adocao por ser mais flexivel e rapido que o MapReduce classico para muitos workloads. Ele entrou no ecossistema Apache e virou uma das principais engines para batch, SQL, machine learning e streaming.

HDFS nasceu no ecossistema Hadoop para armazenar arquivos grandes em clusters on-prem, mantendo storage e computacao proximos. Essa abordagem foi muito comum antes da popularizacao de object storage cloud.

Parquet surgiu no ecossistema Hadoop como formato colunar para analytics. Ele reduziu muito o custo de ler dados em comparacao com formatos linha-a-linha como JSON e CSV.

## Por baixo dos panos do Spark

Spark divide dados em particoes. Cada executor processa particoes em paralelo. O driver coordena o plano de execucao e envia tarefas aos executors.

Operacoes estreitas, como `map` e `filter`, podem rodar sem mover dados entre nos. Operacoes largas, como `groupBy` e alguns joins, causam shuffle. Shuffle redistribui dados pela rede e costuma ser a parte mais cara do job.

Spark SQL usa otimizador Catalyst para transformar uma consulta logica em plano fisico. Com arquivos colunares como Parquet, ele consegue ler apenas colunas necessarias e aplicar filtros de forma mais eficiente.

## Por baixo dos panos do HDFS

HDFS divide arquivos em blocos grandes e replica esses blocos entre datanodes. O namenode mantem os metadados: quais arquivos existem e onde estao seus blocos.

A vantagem classica e data locality: o processamento tenta rodar perto de onde os blocos estao. A desvantagem e o acoplamento entre storage e compute, que torna crescimento e operacao mais rigidos.

## Metastore/catalogo

Arquivos no lake nao bastam para uma plataforma consultavel. E preciso registrar metadados: nome logico da tabela, localizacao dos arquivos, formato, schema e particoes.

Esse papel e do metastore/catalogo. No ambiente local, Hive Metastore e uma escolha classica. Em cloud, alternativas comuns sao AWS Glue Data Catalog, Unity Catalog, Polaris/Nessie ou catalogos especificos de Iceberg/Delta.

O `_delta_log` de uma tabela Delta, que aparece no capitulo lakehouse, registra transacoes daquela tabela, mas nao substitui sozinho um catalogo corporativo. O catalogo responde "quais tabelas existem e onde estao"; o log transacional responde "qual versao desta tabela e valida".

## Parquet

Parquet armazena dados por coluna, com estatisticas e compressao. Em analytics, normalmente voce le poucas colunas de muitas linhas. Por isso Parquet costuma ser muito mais eficiente que JSON cru.

JSON continua util como formato de entrada flexivel. Parquet e melhor como formato curado para consulta.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Flink | Forte em streaming e tambem batch. |
| Trino | Excelente para SQL federado e consultas interativas, nao substitui todos os jobs Spark. |
| Dask | Processamento distribuido em Python, comum em ciencia de dados. |
| Ray | Computacao distribuida geral, muito usado em ML. |
| BigQuery / Snowflake | Warehouses gerenciados; reduzem operacao, mas mudam custo e dependencia de provedor. |

## Quando usar

Use Spark quando o volume, o formato ou o tipo de transformacao passou do limite confortavel de um banco local ou warehouse pequeno.

Evite Spark para tarefas pequenas. O overhead de cluster, configuracao e shuffle pode ser maior que o ganho.

## Como isso aparece no projeto

O capitulo 08 usa HDFS como landing zone on-prem, Spark para processar JSON e Parquet como saida curada. O objetivo e mostrar a mudanca de paradigma: de tabelas de banco para arquivos distribuidos.

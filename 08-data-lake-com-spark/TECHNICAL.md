# Complemento técnico — Spark, HDFS, Metastore e Parquet

## O que este capítulo aprofunda

Este capítulo sai do warehouse pequeno e entra em dados semi-estruturados em escala. A primeira solucao da empresa e aproveitar infraestrutura on-prem existente com HDFS e processamento distribuído com Spark.

## Pequena história

Apache Spark nasceu no AMPLab da UC Berkeley no fim da década de 2000 e ganhou muita adocao por ser mais flexível e rapido que o MapReduce classico para muitos workloads. Ele entrou no ecossistema Apache e virou uma das principais engines para batch, SQL, machine learning e streaming.

HDFS nasceu no ecossistema Hadoop para armazenar arquivos grandes em clusters on-prem, mantendo storage e computacao proximos. Essa abordagem foi muito comum antes da popularizacao de object storage cloud.

Parquet surgiu no ecossistema Hadoop como formato colunar para analytics. Ele reduziu muito o custo de ler dados em comparacao com formatos linha-a-linha como JSON e CSV.

## Por baixo dos panos do Spark

Spark divide dados em partições. Cada executor processa partições em paralelo. O driver coordena o plano de execução e envia tarefas aos executors.

Operações estreitas, como `map` e `filter`, podem rodar sem mover dados entre nos. Operações largas, como `groupBy` e alguns joins, causam shuffle. Shuffle redistribui dados pela rede e costuma ser a parte mais cara do job.

Spark SQL usa otimizador Catalyst para transformar uma consulta lógica em plano físico. Com arquivos colunares como Parquet, ele consegue ler apenas colunas necessarias e aplicar filtros de forma mais eficiente.

## Por baixo dos panos do HDFS

HDFS divide arquivos em blocos grandes e replica esses blocos entre datanodes. O namenode mantém os metadados: quais arquivos existem é onde estao seus blocos.

A vantagem classica e data locality: o processamento tenta rodar perto de onde os blocos estao. A desvantagem e o acoplamento entre storage e compute, que torna crescimento e operação mais rigidos.

## Metastore/catálogo

Arquivos no lake não bastam para uma plataforma consultavel. E preciso registrar metadados: nome lógico da tabela, localizacao dos arquivos, formato, schema e partições.

Esse papel e do metastore/catálogo. No ambiente local, Hive Metastore é uma escolha classica. Em cloud, alternativas comuns são AWS Glue Data Catalog, Unity Catalog, Polaris/Nessie ou catálogos especificos de Iceberg/Delta.

O `_delta_log` de uma tabela Delta, que aparece no capítulo lakehouse, registra transações daquela tabela, mas não substitui sozinho um catálogo corporativo. O catálogo responde "quais tabelas existem é onde estao"; o log transacional responde "qual versão desta tabela e valida".

## Parquet

Parquet armazena dados por coluna, com estatisticas e compressao. Em analytics, normalmente você le poucas colunas de muitas linhas. Por isso Parquet costuma ser muito mais eficiente que JSON cru.

JSON contínua util como formato de entrada flexível. Parquet é melhor como formato curado para consulta.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Flink | Forte em streaming e também batch. |
| Trino | Excelente para SQL federado e consultas interativas, não substitui todos os jobs Spark. |
| Dask | Processamento distribuído em Python, comum em ciencia de dados. |
| Ray | Computacao distribuída geral, muito usado em ML. |
| BigQuery / Snowflake | Warehouses gerenciados; reduzem operação, mas mudam custo e dependencia de provedor. |

## Quando usar

Use Spark quando o volume, o formato ou o tipo de transformacao passou do limite confortavel de um banco local ou warehouse pequeno.

Evite Spark para tarefas pequenas. O overhead de cluster, configuracao e shuffle pode ser maior que o ganho.

## Como isso aparece no projeto

O capítulo 08 usa HDFS como landing zone on-prem, Spark para processar JSON e Parquet como saída curada. O objetivo e mostrar a mudança de paradigma: de tabelas de banco para arquivos distribuidos.

## 📚 Referências

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/) — referência oficial com guias de SQL, DataFrames e tuning.
- [Parquet Format Specification](https://parquet.apache.org/documentation/latest/) — especificação técnica do formato colunar.
- [HDFS Architecture Guide](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) — design do HDFS com blocos, replicação e namenode.

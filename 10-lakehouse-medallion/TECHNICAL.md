# Complemento tecnico - Delta Lake, lakehouse e Medallion

## O que este capitulo aprofunda

Este capitulo adiciona confiabilidade de warehouse sobre um data lake. O problema nao e mais apenas armazenar e processar arquivos; e garantir transacoes, schema, historico e leituras consistentes.

## Pequena historia

Data lakes cresceram com Hadoop e depois com object storage. Eles eram baratos e flexiveis, mas frequentemente viravam data swamps: muitos arquivos, pouca governanca e baixa confiabilidade.

Lakehouse surgiu como resposta a essa dor: manter storage barato em arquivos, mas adicionar recursos de banco analitico. Delta Lake foi criado pela Databricks e aberto no fim da decada de 2010. Apache Iceberg e Apache Hudi sao outras respostas importantes ao mesmo problema.

Medallion, com camadas bronze, silver e gold, foi popularizado no ecossistema Databricks como uma forma simples de organizar qualidade progressiva dos dados.

## Por baixo dos panos do Delta

Uma tabela Delta e composta por arquivos Parquet mais um log transacional em `_delta_log`. Esse log registra commits, arquivos adicionados, arquivos removidos, schema e metadados.

Quando uma query le a tabela, ela nao lista qualquer arquivo solto e assume que tudo vale. Ela interpreta o log e descobre qual conjunto de arquivos representa a versao atual.

Isso permite:

- commits atomicos;
- time travel;
- schema enforcement;
- schema evolution controlada;
- `MERGE` para upsert;
- limpeza posterior de arquivos antigos.

Delta Lake resolve a consistencia transacional da tabela, mas a plataforma ainda precisa de catalogo/metastore para descoberta e acesso. O metastore registra nomes logicos, schemas, localizacoes e particoes. O `_delta_log` registra os commits e a versao valida de cada tabela.

## Medallion

Bronze guarda o dado cru, fiel a origem. Deve preservar historico e facilitar reprocessamento.

Silver limpa, tipa, deduplica e aplica regras tecnicas.

Gold modela para consumo: metricas, agregados e tabelas de negocio.

A vantagem e separar responsabilidades. Um erro em regra de negocio nao deve destruir a camada bronze; uma mudanca de schema deve ser tratada antes de chegar ao BI.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Apache Iceberg | Tabela lakehouse aberta, muito forte em catalogos e evolucao de schema/particao. |
| Apache Hudi | Forte em upserts e ingestao incremental. |
| Delta Lake | Muito integrado a Spark e Databricks, simples para demonstrar ACID no lake. |
| Hive tables | Historicas no ecossistema Hadoop, mas menos robustas para transacoes modernas. |

## Quando usar

Use lakehouse quando voce precisa de escala e custo de lake, mas nao aceita arquivos soltos sem governanca.

Evite quando o problema e pequeno e um warehouse simples resolve. Lakehouse adiciona catalogo, logs, manutencao e escolhas de engine.

## Como isso aparece no projeto

O capitulo 10 transforma o lake migrado para S3/MinIO em uma plataforma mais confiavel. A camada gold passa a ser base para BI e para consumo historico, enquanto bronze e silver sustentam reprocessamento e qualidade.

# Complemento técnico - Delta Lake, lakehouse e Medallion

## O que este capítulo aprofunda

Este capítulo adiciona confiabilidade de warehouse sobre um data lake. O problema não é mais apenas armazenar e processar arquivos; e garantir transações, schema, histórico e leituras consistentes.

## Pequena história

Data lakes cresceram com Hadoop e depois com object storage. Eles eram baratos e flexíveis, mas frequentemente viravam data swamps: muitos arquivos, pouca governanca e baixa confiabilidade.

Lakehouse surgiu como resposta a essa dor: manter storage barato em arquivos, mas adicionar recursos de banco analítico. Delta Lake foi criado pela Databricks e aberto no fim da década de 2010. Apache Iceberg e Apache Hudi são outras respostas importantes ao mesmo problema.

Medallion, com camadas bronze, silver e gold, foi popularizado no ecossistema Databricks como uma forma simples de organizar qualidade progressiva dos dados.

## Por baixo dos panos do Delta

Uma tabela Delta e composta por arquivos Parquet mais um log transacional em `_delta_log`. Esse log registra commits, arquivos adicionados, arquivos removidos, schema e metadados.

Quando uma query le a tabela, ela não lista qualquer arquivo solto e assume que tudo vale. Ela interpreta o log e descobre qual conjunto de arquivos representa a versão atual.

Isso permite:

- commits atomicos;
- time travel;
- schema enforcement;
- schema evolution controlada;
- `MERGE` para upsert;
- limpeza posterior de arquivos antigos.

Delta Lake resolve a consistência transacional da tabela, mas a plataforma ainda precisa de catálogo/metastore para descoberta e acesso. O metastore registra nomes logicos, schemas, localizacoes e partições. O `_delta_log` registra os commits e a versão valida de cada tabela.

## Medallion

Bronze guarda o dado cru, fiel a origem. Deve preservar histórico e facilitar reprocessamento.

Silver limpa, tipa, deduplica e aplica regras técnicas.

Gold modela para consumo: métricas, agregados e tabelas de negócio.

A vantagem e separar responsabilidades. Um erro em regra de negócio não deve destruir a camada bronze; uma mudança de schema deve ser tratada antes de chegar ao BI.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| Apache Iceberg | Tabela lakehouse aberta, muito forte em catálogos e evolucao de schema/partição. |
| Apache Hudi | Forte em upserts e ingestao incremental. |
| Delta Lake | Muito integrado a Spark e Databricks, simples para demonstrar ACID no lake. |
| Hive tables | Históricas no ecossistema Hadoop, mas menos robustas para transações modernas. |

## Quando usar

Use lakehouse quando você precisa de escala e custo de lake, mas não aceita arquivos soltos sem governanca.

Evite quando o problema e pequeno e um warehouse simples resolve. Lakehouse adiciona catálogo, logs, manutenção e escolhas de engine.

## Como isso aparece no projeto

O capítulo 10 transforma o lake migrado para S3/MinIO em uma plataforma mais confiável. A camada gold passa a ser base para BI e para consumo histórico, enquanto bronze e silver sustentam reprocessamento e qualidade.

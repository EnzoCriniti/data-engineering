# Build — Capítulo 10: como construir o Lakehouse Medallion

> Guia **avançado e detalhado**. Status **ambiente base**: roteiro de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Construir uma camada lakehouse transacional (Delta Lake) sobre o object storage do cap. 09, organizada em Medallion (bronze/silver/gold), com métricas gold equivalentes aos marts do warehouse — para então migrar o consumo do warehouse para o lakehouse.

## Pré-requisitos de conhecimento

- O storage em S3/MinIO do [cap. 09](../09-migracao-hdfs-para-s3).
- Delta Lake (`_delta_log`, ACID, time travel, `MERGE`), Spark, Trino.
- Os marts do [cap. 04](../04-elt-batch-com-python)/dbt como referência de equivalência.

## Estado inicial

Estado final do cap. 09: dados raw/curados em object storage, consultáveis por Trino. Faltam garantias transacionais e uma organização por camadas de qualidade.

## Passo 1 — Ambiente (`docker-compose.yml`)

MinIO (storage), Spark com a biblioteca Delta, Trino (catálogo Delta/Hive), metastore, Airflow e Metabase. Montar `spark/jobs/` e `trino/catalog/`.

## Passo 2 — Bronze (`spark/jobs/bronze.py`)

Ingerir o dado já em S3 numa tabela Delta **bronze**, fiel à origem: sem limpeza, só estrutura mínima e metadados de ingestão (timestamp, fonte). Bronze é o ponto de auditoria — preserva exatamente o que entrou.

## Passo 3 — Silver (`spark/jobs/silver.py`)

Ler bronze, tipar colunas, deduplicar (por chave natural), aplicar regras técnicas de qualidade e normalizar. Usar `MERGE` para tornar a carga idempotente. Schema enforcement do Delta garante que dado fora do esquema seja rejeitado.

## Passo 4 — Gold (`spark/jobs/gold.py`)

Construir as tabelas de métricas de negócio (ex.: receita diária, top produtos), **equivalentes aos marts** dos capítulos anteriores. Gold é o que o BI consome.

## Passo 5 — Catálogo e Trino (`trino/catalog/`)

Registrar bronze/silver/gold no metastore e configurar o catálogo Delta no Trino, para consulta SQL federada.

## Passo 6 — Migração e equivalência

1. ler os dados já em S3/MinIO do cap. 09;
2. recriar bronze em Delta, preservando fidelidade;
3. construir silver com tipagem, deduplicação e regras;
4. construir gold com métricas equivalentes aos marts;
5. registrar tudo no catálogo;
6. comparar gold vs marts/warehouse antes de apontar o BI;
7. manter a camada antiga como fallback até a validação passar.

## Validações (definição de pronto)

- [ ] bronze/silver/gold são tabelas Delta com `_delta_log` presente.
- [ ] Recarga via `MERGE` é idempotente (não duplica).
- [ ] As métricas gold batem com os marts do warehouse anterior.
- [ ] Time travel funciona (consultar uma versão anterior da tabela).

## Estado final (gabarito para o próximo capítulo)

Lakehouse confiável e transacional, com BI apontando para gold. Mas ainda é batch — a próxima dor é capturar mudanças continuamente. Gancho para o [cap. 11: CDC com Debezium](../11-cdc-com-debezium).

# Gabarito de estado - Capítulo 10

## Objetivo do capítulo

Transformar o data lake em lakehouse confiável com Delta Lake e arquitetura Medallion.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 09:

- MinIO com dados crus;
- dados curados em Parquet;
- dados migrados para S3/MinIO;
- metastore/catálogo do lake;
- jobs Spark basicos;
- necessidade de transações, schema enforcement e time travel.

## Etapas do capítulo

1. Subir stack lakehouse: MinIO, Spark, Airflow, Trino e Metabase.
2. Migrar dados crus para bronze Delta.
3. Criar silver com limpeza, tipagem e deduplicação.
4. Criar gold com métricas de negócio.
5. Registrar tabelas no metastore/catálogo.
6. Configurar query engine para consultar gold.
7. Apontar BI para a camada consultavel.

## Estado final esperado

Ao final, deve existir:

- bronze Delta;
- silver Delta;
- gold Delta;
- `_delta_log` nas tabelas Delta;
- tabelas registradas no catálogo;
- gold consultavel por SQL;
- métricas equivalentes aos marts anteriores.

## Validações

- Tabelas Delta possuem transaction log.
- Gold bate com marts/warehouse anteriores para métricas principais.
- Reprocessamento não duplica dados.
- Schema enforcement rejeita dado inválido.
- Query engine consegue ler a gold.
- Catálogo aponta para as localizacoes corretas das tabelas.

## Como o proximo capítulo usa este estado

O capítulo 11 usa o lakehouse como destino de mudanças capturadas via CDC, reduzindo a necessidade de recargas batch completas.

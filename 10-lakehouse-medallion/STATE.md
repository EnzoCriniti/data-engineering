# Gabarito de estado - Capitulo 10

## Objetivo do capitulo

Transformar o data lake em lakehouse confiavel com Delta Lake e arquitetura Medallion.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 09:

- MinIO com dados crus;
- dados curados em Parquet;
- dados migrados para S3/MinIO;
- metastore/catalogo do lake;
- jobs Spark basicos;
- necessidade de transacoes, schema enforcement e time travel.

## Etapas do capitulo

1. Subir stack lakehouse: MinIO, Spark, Airflow, Trino e Metabase.
2. Migrar dados crus para bronze Delta.
3. Criar silver com limpeza, tipagem e deduplicacao.
4. Criar gold com metricas de negocio.
5. Registrar tabelas no metastore/catalogo.
6. Configurar query engine para consultar gold.
7. Apontar BI para a camada consultavel.

## Estado final esperado

Ao final, deve existir:

- bronze Delta;
- silver Delta;
- gold Delta;
- `_delta_log` nas tabelas Delta;
- tabelas registradas no catalogo;
- gold consultavel por SQL;
- metricas equivalentes aos marts anteriores.

## Validacoes

- Tabelas Delta possuem transaction log.
- Gold bate com marts/warehouse anteriores para metricas principais.
- Reprocessamento nao duplica dados.
- Schema enforcement rejeita dado invalido.
- Query engine consegue ler a gold.
- Catalogo aponta para as localizacoes corretas das tabelas.

## Como o proximo capitulo usa este estado

O capitulo 11 usa o lakehouse como destino de mudancas capturadas via CDC, reduzindo a necessidade de recargas batch completas.

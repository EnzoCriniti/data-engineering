# Capitulo 09 - Migracao de HDFS para S3

> De onde viemos: a plataforma ja tem lake/lakehouse, streaming e base de features de ML. Agora aparece uma dor comum em empresas reais: existe um legado Hadoop/HDFS que precisa migrar gradualmente para object storage.

## Cenario de negocio

Antes da plataforma moderna em S3/MinIO, a NuvemStore tinha um data lake antigo em HDFS, mantido em um cluster on-prem. Esse legado ainda guarda historico operacional e algumas particoes recentes usadas por jobs criticos.

O problema: operar HDFS ficou caro e rigido. Storage e compute escalam juntos, manutencao do cluster exige cuidado, e a empresa quer aproximar o legado do padrao moderno de lake/lakehouse em object storage.

A migracao nao pode ser "desliga HDFS e liga S3" de uma vez. Durante um periodo, os dois mundos convivem:

- HDFS como zona quente/legada para dados ainda muito acessados;
- S3/MinIO como zona fria e alvo moderno da migracao;
- Spark fazendo leitura/migracao entre as duas zonas;
- Trino/BI consultando sem o usuario precisar saber onde cada particao esta.

## Status desta etapa

Status atual: **ambiente base**.

O compose sobe:

- HDFS namenode e datanode;
- MinIO como destino S3-compatible;
- Spark master e worker;
- Airflow;
- Trino;
- Metabase.

Os jobs `migrate_hdfs_to_s3.py`, `query_federada.py` e `tiering.py`, alem dos catalogos Trino, serao implementados depois.

## Como esta etapa migra a anterior

Storage hibrido aqui nao significa "S3 nao basta". Significa simular uma transicao real: a empresa ja tinha HDFS, mas quer migrar para S3 sem interromper consumidores.

Plano de migracao:

1. inventariar particoes/tabelas ainda no HDFS legado;
2. classificar dados por criticidade e padrao de acesso;
3. migrar historico frio para MinIO/S3;
4. manter temporariamente dados quentes ou jobs sensiveis em HDFS;
5. configurar query engine para federar HDFS e S3;
6. validar contagens por particao antes e depois da migracao;
7. reduzir gradualmente dependencia do HDFS ate ele virar excecao, nao padrao.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

## Conceitos principais

- HDFS como legado on-prem.
- S3/object storage como alvo moderno.
- Data locality vs separacao compute/storage.
- Migracao gradual de storage.
- Tiering quente/frio durante transicao.
- Federacao de queries.
- Engenharia de custo aplicada a dados.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## Fim da trilha

Esta etapa fecha a discussao de arquitetura fisica: uma plataforma de dados nao evolui apenas escolhendo a melhor tecnologia do zero; ela tambem precisa migrar legados, preservar consumidores e validar dados durante a transicao.

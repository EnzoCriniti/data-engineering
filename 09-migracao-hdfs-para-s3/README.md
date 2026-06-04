# Capítulo 09 — Migração de HDFS para S3 🟡

> **De onde viemos:** no [cap. 08](../08-data-lake-com-spark) montamos um data lake on-prem em HDFS. Ele funciona, mas operar o cluster é caro e rígido — storage e compute escalam juntos. Agora aparece uma dor comum em empresas reais: migrar gradualmente esse legado HDFS para object storage, sem interromper os consumidores.

## Cenário de negócio

A NuvemStore tem um data lake em HDFS, num cluster on-prem. Esse legado guarda histórico operacional e algumas partições recentes usadas por jobs críticos.

O problema: operar HDFS ficou caro e rígido. Storage e compute escalam juntos, a manutenção do cluster exige cuidado constante, e a empresa quer aproximar o legado do padrão moderno de object storage (S3/MinIO), onde storage e compute são desacoplados.

A migração não pode ser "desliga HDFS e liga S3" de uma vez. Durante um período, os dois mundos convivem:

- **HDFS** como zona quente/legada, para dados ainda muito acessados;
- **S3/MinIO** como alvo moderno da migração;
- **Spark** lendo e migrando entre as duas zonas;
- **Trino/BI** consultando sem o usuário precisar saber onde cada partição está.

## Conceitos

**HDFS legado vs object storage moderno.** O HDFS acopla storage e compute (data locality); o S3 os separa — você escala armazenamento e processamento de forma independente, paga só pelo que usa. É a virada arquitetural que viabiliza o lakehouse do cap. 10.

**Migração gradual e tiering.** Mover tudo de uma vez é arriscado. Classifica-se o dado por padrão de acesso: o frio/histórico vai primeiro para o S3; o quente e os jobs sensíveis ficam temporariamente em HDFS. O tiering quente/frio reduz risco e custo durante a transição.

**Federação de queries.** Um query engine (Trino) consulta HDFS e S3 ao mesmo tempo, escondendo do consumidor onde cada partição vive. É o que permite migrar por baixo sem quebrar dashboards.

**Reconciliação.** Antes e depois de mover cada partição, comparam-se contagens e amostras. Migração de dados sem validação é perda de dados silenciosa.

> Detalhamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base.** O compose sobe HDFS, MinIO, Spark, Airflow, Trino e Metabase. Os jobs (`migrate_hdfs_to_s3.py`, `query_federada.py`, `tiering.py`) e os catálogos do Trino são o próximo passo de implementação.

Para subir o ambiente híbrido (HDFS + MinIO + Spark + Trino), veja o **[RUNBOOK.md](./RUNBOOK.md)**.

## A dor que sobra

Com o storage já em object storage e o compute desacoplado, falta dar ao lake as garantias do warehouse — transações, schema enforcement, time travel. → [Capítulo 10: Lakehouse com arquitetura Medallion](../10-lakehouse-medallion).

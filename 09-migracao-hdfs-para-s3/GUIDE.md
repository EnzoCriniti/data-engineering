# Cap. 09 — Migração HDFS para S3: desacoplando storage e compute

> **Aula deste capítulo.** Você desacopla storage de compute migrando de **HDFS** para **object storage** (MinIO/S3) e adiciona **Trino** como motor de consulta federado. A orientação está aqui; o código do `migrate_hdfs_to_s3.py` e a config do catálogo Trino estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (S3a, rename não-atômico, connector Hive do Trino) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O HDFS do capítulo 08 funciona, mas acopla storage e compute: para mais espaço, precisa mais nós de cluster. A operação é cara (namenode, replicação, balanceamento de blocos). A indústria migrou massivamente para object storage (S3/MinIO) — elástico, barato para dados frios, e desacoplado do motor de processamento.

Este capítulo executa essa migração: HDFS vira legado, MinIO (S3-compatible) vira o storage primário, e Trino entra como motor de consulta SQL federado.

## Pré-requisitos

- **Capítulo anterior:** 08 concluído (lake on-prem com Spark).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Object storage vs filesystem distribuído

HDFS é um filesystem: diretórios, blocos, data locality. S3 é object storage: buckets, chaves, sem hierarquia real. S3 desacopla storage de compute — escala independentemente, cobra por uso, e é operacionalmente mais simples.

Tradeoff: latência de rede maior (dados não estão "perto" do compute), e rename atômico não é natural (afeta como formatos lakehouse fazem commit).

**Exemplo trabalhado — desacoplar storage e compute, em números.** No HDFS, storage e compute moram nos mesmos nós. Numa Black Friday você precisa de 10x mais *processamento* por algumas horas — mas no HDFS isso significa adicionar nós que vêm com disco junto, então você paga por storage que não precisava, e depois do pico esse hardware fica ocioso. Com S3, o storage é um serviço à parte: você sobe 10x mais executors Spark/Trino lendo do *mesmo* bucket por 3 horas e os desliga depois, sem mexer em um byte de armazenamento. O custo de storage não muda; só o compute escala e encolhe sob demanda. Esse desacoplamento é a razão econômica de a indústria ter migrado em massa.

### Tiering: dados quentes e frios

Tiering define política de movimentação por padrão de acesso:
- **Hot (HDFS)**: dados recentes e muito acessados — mantém temporariamente no legado.
- **Cold (MinIO/S3)**: histórico e dados pouco acessados — custo baixo, latência aceitável.

A migração não precisa ser big-bang. Dados frios migram primeiro; dados quentes migram quando o legado é descomissionado.

### MinIO como S3 local

MinIO implementa a API S3 fielmente. Spark, Trino e outras ferramentas conectam via S3a:// sem saber se é AWS S3 ou MinIO. Perfeito para desenvolvimento local e portfolio.

### Trino: SQL federado

Trino (ex-PrestoSQL) consulta dados de múltiplas fontes via SQL: S3 (com Hive connector), Postgres, MySQL, Kafka. Não armazena dados — é um motor de query puro. Ideal para consultar o lake sem Spark.

**Exemplo trabalhado — uma query, duas fontes.** O analista quer "entregas (no lake/MinIO) cruzadas com o cadastro de clientes (que ainda vive no Postgres OLTP)". Sem federação, alguém teria que exportar uma das duas e juntar na mão. Com Trino, os dois aparecem como catálogos — `hive.default.entregas` e `postgres.public.cliente` — e um único `SELECT ... FROM hive.default.entregas e JOIN postgres.public.cliente c ON ...` roda o JOIN buscando cada metade da sua fonte nativa, sem mover nada para um lugar comum antes. Trino não guarda dado nenhum: ele empurra os filtros para cada fonte e junta os resultados em memória. É SQL único sobre um lake e um banco que nunca se falaram.

---

## Etapa 1 — Adicionar MinIO e Trino ao ambiente

### O que fazer
Expandir docker-compose com: MinIO (porta 9000 API, 9001 console), Trino (porta 8082), catálogo Hive apontando para MinIO. Manter HDFS e Spark do capítulo 08 para demonstrar o ambiente híbrido.

### ⚠️ Armadilhas
- MinIO precisa de `MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD` explícitos.
- Trino precisa de catalog config em `trino/catalog
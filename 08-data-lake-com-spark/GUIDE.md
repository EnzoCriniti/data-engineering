# Cap. 08 — Data lake com Spark: processamento distribuído on-prem

> **Aula deste capítulo.** Você muda de paradigma — de tabelas em banco para **arquivos distribuídos** processados por **Spark** sobre HDFS, catalogados no Hive Metastore. A orientação está aqui; o código do `ingest_to_lake.py` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (driver/executors, shuffle, blocos HDFS, layout colunar do Parquet) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O warehouse DuckDB/Postgres funciona para os volumes atuais, mas não escala para dados semi-estruturados (JSONs de GPS, logs de aplicação) nem para volumes de terabytes. A empresa decide investir em infraestrutura on-prem existente: cluster HDFS para storage e Spark para processamento.

Este capítulo muda o paradigma: de tabelas em banco para **arquivos distribuídos em filesystem**, processados por uma engine paralela. É a transição de warehouse para data lake.

## Pré-requisitos

- **Capítulo anterior:** 07 concluído (Airflow orquestrando).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Data lake vs warehouse

Warehouse armazena dados estruturados em tabelas otimizadas para query. Data lake armazena dados de qualquer formato (JSON, CSV, Parquet, imagens) em filesystem — mais flexível, mais barato, mas sem garantias de consistência ou schema sem camadas adicionais.

### Spark: processamento distribuído

Spark divide dados em partições e processa em paralelo. O **driver** coordena o plano de execução; os **executors** processam partições. Operações narrow (map, filter) não movem dados entre nós. Operações wide (groupBy, join) causam **shuffle** — redistribuição pela rede, geralmente a parte mais cara.

**Exemplo trabalhado — narrow vs wide, e por que o shuffle dói.** Você tem 100GB de eventos de GPS espalhados em 800 partições, uma por bloco, cada uma num executor. Um `filter(status == 'entregue')` é *narrow*: cada executor processa sua partição localmente, nada cruza a rede — 800 tarefas independentes, rápido. Já um `groupBy(entregador_id).count()` é *wide*: todas as linhas do mesmo entregador precisam acabar no mesmo executor para serem contadas, então o Spark **embaralha** os 100GB pela rede para reagrupar por chave. É por isso que a mesma quantidade de dados leva segundos no filter e minutos no groupBy — não é o volume, é o movimento. Otimizar Spark é, em grande parte, evitar ou reduzir shuffles.

### HDFS: storage distribuído

HDFS divide arquivos em blocos grandes (128MB default), replica em múltiplos datanodes. O namenode mantém metadados. Vantagem: data locality (processamento perto do dado). Desvantagem: acopla storage e compute.

### Parquet: formato colunar

Analytics tipicamente lê poucas colunas de muitas linhas. Parquet armazena por coluna, com compressão e estatísticas. Uma query que seleciona 3 colunas de uma tabela de 50 lê apenas ~6% dos dados vs 100% em JSON linha-a-linha.

**Exemplo trabalhado — o GROUP BY que lê 6% do disco.** A tabela `entregas` tem 50 colunas e 200 milhões de linhas. A pergunta é "tempo médio de entrega por dia", que toca só `data_ocorrencia` e `duracao_min`. Em **JSON** (linha-a-linha), o Spark precisa ler e parsear todo o arquivo — as 50 colunas de cada linha — só para descartar 48. Em **Parquet** (colunar), as colunas vivem em blocos separados: o leitor pula direto para os blocos de `data_ocorrencia` e `duracao_min` e ignora fisicamente o resto do arquivo. Some o particionamento por data (lê só os dias pedidos) e as estatísticas por bloco (pula blocos fora do filtro), e a mesma query passa de varrer terabytes para varrer gigabytes. O formato, sozinho, muda a ordem de grandeza do custo.

### Metastore/catálogo

Arquivos no lake não bastam — é preciso registrar metadados: nome lógico da tabela, localização dos arquivos, schema, partições. O Hive Metastore é a escolha clássica. Sem catálogo, o lake vira um "data swamp" de arquivos sem descobribilidade.

---

## Etapa 1 — Criar o ambiente com HDFS, Spark e Hive Metastore

### O que fazer
Compose com: namenode, datanode (HDFS), spark-master, spark-worker, hive-metastore (MySQL ou Postgres como backend), e o Postgres OLTP como fonte.

### ⚠️ Armadilhas
- HDFS em Docker é pesado em memória. Configurar namenode e datanode com limites razoáveis (`-Xmx512m`).
- Hive Metastore precisa de schema inicializado (`schematool -dbType postgres -initSchema`).

---

## Etapa 2 
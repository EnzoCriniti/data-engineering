# Confiabilidade e observabilidade

## Principio

Observabilidade entra conforme a plataforma amadurece. O objetivo nao e instalar uma ferramenta para cada problema, e sim mostrar quais sinais precisam existir.

## Sinais por camada

| Camada | Sinais minimos |
| --- | --- |
| ELT batch | linhas lidas, linhas gravadas, tempo de execucao, erro por etapa. |
| dbt | testes, freshness, docs, lineage e falhas de modelo. |
| API externa | status HTTP, timeout, rate limit, pagina atual, checkpoint. |
| Airflow | run status, task logs, retry count, SLA, duracao. |
| Lake | arquivos gerados, particoes, schema e registro no metastore. |
| Migracao HDFS -> S3 | contagem por particao, bytes migrados, query comparativa. |
| Lakehouse | versao Delta, schema enforcement, time travel e commits. |
| CDC | connector status, lag, offsets, eventos por tabela. |
| Streaming | consumer lag, watermark, checkpoint e estado. |
| ML | drift de features, nulos, distribuicao e data freshness. |

## Qualidade de dados

Controles minimos:

- contagem origem/destino;
- checagem de duplicidade por chave;
- `not_null` em colunas criticas;
- `relationships` entre fato e dimensoes;
- validacao de schema em payload externo;
- validacao de particoes no lake;
- comparacao de metricas antes/depois de migracoes.

## Alertas

Alertas importantes:

- pipeline nao rodou;
- carga atrasada;
- queda brusca de linhas;
- aumento de nulos;
- falha de conector CDC;
- lag alto em streaming;
- feature table desatualizada;
- BI apontando para tabela antiga/legada.

## Continuidade entre capitulos

Cada capitulo deve fechar com:

- estado final claro;
- validacao minima;
- o que virou legado;
- o que vira entrada do proximo capitulo.

Esse controle evita que uma tecnologia seja demonstrada uma vez e suma da historia sem consequencia.

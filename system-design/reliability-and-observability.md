# Confiabilidade e observabilidade

## Principio

Observabilidade entra conforme a plataforma amadurece. O objetivo não e instalar uma ferramenta para cada problema, e sim mostrar quais sinais precisam existir.

## Sinais por camada

| Camada | Sinais minimos |
| --- | --- |
| ELT batch | linhas lidas, linhas gravadas, tempo de execução, erro por etapa. |
| dbt | testes, freshness, docs, lineage e falhas de modelo. |
| API externa | status HTTP, timeout, rate limit, pagina atual, checkpoint. |
| Airflow | run status, task logs, retry count, SLA, duracao. |
| Lake | arquivos gerados, partições, schema e registro no metastore. |
| Migracao HDFS -> S3 | contagem por partição, bytes migrados, query comparativa. |
| Lakehouse | versão Delta, schema enforcement, time travel e commits. |
| CDC | connector status, lag, offsets, eventos por tabela. |
| Streaming | consumer lag, watermark, checkpoint e estado. |
| ML | drift de features, nulos, distribuicao e data freshness. |

## Qualidade de dados

Controles minimos:

- contagem origem/destino;
- checagem de duplicidade por chave;
- `not_null` em colunas criticas;
- `relationships` entre fato e dimensoes;
- validação de schema em payload externo;
- validação de partições no lake;
- comparacao de métricas antes/depois de migracoes.

## Alertas

Alertas importantes:

- pipeline não rodou;
- carga atrasada;
- queda brusca de linhas;
- aumento de nulos;
- falha de conector CDC;
- lag alto em streaming;
- feature table desatualizada;
- BI apontando para tabela antiga/legada.

## Continuidade entre capítulos

Cada capítulo deve fechar com:

- estado final claro;
- validação minima;
- o que virou legado;
- o que vira entrada do proximo capítulo.

Esse controle evita que uma tecnologia seja demonstrada uma vez e suma da história sem consequencia.

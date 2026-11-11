# Índice técnico

Os capítulos detalham as cinco fases da [história da NuvemStore](../README.md#como-a-nuvemstore-evolui). Em cada capítulo, o README explica a decisão, o RUNBOOK mostra como executar, o GUIDE orienta a implementação, a SOLUTION apresenta a solução e o TECHNICAL aprofunda a tecnologia. Veja o [padrão do repositório](./padrao-do-repositorio.md) para os critérios de conclusão.

## 1. Do checkout à receita diária

| Capítulo | Tema | Status | Papel na história |
| --- | --- | --- | --- |
| [00](../00-modelagem-transacional) | Modelagem transacional | Em validação | Define a origem OLTP e o seeder compartilhado. |
| [01](../01-modelagem-dimensional) | Modelagem dimensional | Documentado | Desenha o star schema e os conceitos OLAP. |
| [02](../02-dimensional-no-oltp) | Dimensional no mesmo OLTP | Em validação | Mostra analytics em outro schema, mas ainda dividindo recursos com a aplicação. |
| [03](../03-warehouse-dedicado) | Warehouse dedicado | Em validação | Separa OLTP e warehouse em bancos diferentes e migra dados. |
| [04](../04-elt-batch-com-python) | ELT batch com Python | Em validação | Extrai do OLTP, carrega raw no DuckDB e cria marts. |

## 2. Entregas com múltiplas fontes

| Capítulo | Tema | Status | Papel na história |
| --- | --- | --- | --- |
| [05](../05-transformacao-com-dbt) | Transformação com dbt | Em validação | Reimplementa transformações manuais como modelos testáveis. |
| [06](../06-ingestao-api-externa) | Ingestão batch de API externa | Em validação | Adiciona uma fonte externa batch: transportadora. |
| [07](../07-orquestracao-com-airflow) | Orquestração com Airflow | Em validação | Coordena OLTP, API externa, dbt, retries e backfill. |

## 3. Histórico de navegação

| Capítulo | Tema | Status | Papel na história |
| --- | --- | --- | --- |
| [08](../08-data-lake-com-spark) | Data Lake on-prem com HDFS | Documentado | Sobe HDFS, Spark e metastore/catálogo para histórico, JSON e dados semi-estruturados. |
| [09](../09-migracao-hdfs-para-s3) | Migração HDFS para S3 | Documentado | Simula legado HDFS e migração gradual para MinIO/S3. |
| [10](../10-lakehouse-medallion) | Lakehouse + Medallion | Documentado | Evolui object storage para Delta/Medallion com gold consultável e tabelas catalogadas. |

## 4. Decisões durante o dia

| Capítulo | Tema | Status | Papel na história |
| --- | --- | --- | --- |
| [11](../11-cdc-com-debezium) | CDC com Debezium | Documentado | Sobe Postgres com WAL lógico, Redpanda e Kafka Connect. |
| [12](../12-streaming-kappa) | Streaming Kappa | Documentado | Sobe Redpanda para métricas em tempo real. |
| [13](../13-base-ml-fraude) | Base de ML para fraude | Documentado | Prepara feature table para modelo simples de fraude de pagamentos. |

## 5. Operação confiável

| Capítulo | Tema | Status | Papel na história |
| --- | --- | --- | --- |
| [14](../14-iac-cloud-localstack) | Infra como código (Terraform/LocalStack) | Documentado | Provisiona o storage do lake como código, validado contra nuvem emulada (custo zero). |
| [15](../15-qualidade-contratos-dados) | Qualidade e contratos de dados | Documentado | Portão de qualidade que valida o dado cru na borda antes das camadas confiáveis. |
| [16](../16-observabilidade-pipeline) | Observabilidade do pipeline | Documentado | Mede freshness e volume das tabelas e alerta quando um SLO é violado. |
| [17](../17-capstone-consolidacao) | Capstone de consolidação | Documentado | Descreve a arquitetura consolidada e a galeria de provas planejada. |

## Migrações entre ambientes

Quando uma tecnologia nova entra, ela não deve parecer um ambiente mágico criado do zero. Ela entra como evolução de uma plataforma que já existe.

A narrativa ideal é:

1. subir o ambiente novo;
2. recriar o estado final do capítulo anterior;
3. migrar ou materializar os dados na nova camada;
4. validar contagens e métricas;
5. desligar ou reduzir a camada antiga.

Checklist de passagem entre capítulos:

- o estado final do capítulo anterior está descrito no início do README seguinte ("De onde viemos");
- o capítulo seguinte recria esse estado no próprio compose ou nos seus jobs;
- existe uma validação mínima de equivalência;
- o que fica legado ou fallback está explicitamente documentado;
- nada importante depende de um container antigo ainda rodando.

| Etapa nova | O que reaproveita | O que muda | Como valida |
| --- | --- | --- | --- |
| `05 dbt` | marts SQL do ELT manual | reimplementa transformações como modelos dbt | compara contagens e métricas dos marts antigos vs dbt |
| `06 API externa` | warehouse e marts internos | adiciona staging batch da transportadora | valida idempotência e reconciliação por `pedido_id` |
| `07 Airflow` | OLTP, API externa e dbt | troca execução manual por DAG orquestrado | compara runs manuais vs runs orquestradas |
| `08 Data Lake HDFS` | warehouse, OLTP e API externa | descarrega dados crus/históricos para HDFS, processa com Spark e registra no metastore | compara volume carregado e amostras contra origem/warehouse |
| `09 Migração HDFS -> S3` | lake HDFS legado | migra histórico para S3/MinIO mantendo acesso federado | valida queries federadas e contagens por partição |
| `10 Lakehouse` | dados migrados para object storage e metastore | converte para Delta e organiza bronze/silver/gold | compara gold vs marts anteriores e verifica histórico/catálogo |
| `11 CDC` | OLTP e lakehouse existentes | passa a atualizar por eventos do WAL | compara snapshot inicial e eventos aplicados no destino |
| `12 Streaming` | log/eventos e lakehouse existentes | calcula métricas com janelas em tempo real | compara agregados streaming vs recomputação batch |
| `13 Base ML fraude` | lakehouse, CDC e streaming | materializa feature table para modelo de fraude | valida point-in-time correctness e ausência de duplicidade |

## Controles minimos por maturidade

Para não encher o repositório de ferramentas antes da hora, observabilidade, segurança e qualidade entram de forma incremental:

| Momento | Controle principal | Por que entra aqui |
| --- | --- | --- |
| 04 ELT batch | idempotência e contagem origem/destino | garante que reprocessar não duplica dados. |
| 05 dbt | testes de dados e contratos de schema | SQL vira produto confiável. |
| 06 API externa | checkpoint, validação de payload e tratamento de erro | API falha, muda contrato e pode retornar dados duplicados. |
| 07 Airflow | logs por task, retries, backfill e SLA simples | pipeline vira operação. |
| 08 Lake HDFS | validação de arquivos, partições e registro no metastore | arquivos precisam ser descobertos e auditáveis. |
| 09 Migração HDFS -> S3 | reconciliação por partição e comparação de query | migração sem validação quebra consumidores. |
| 10 Lakehouse | schema enforcement, time travel e auditoria de versão | tabelas passam a ter contrato transacional. |
| 11 CDC | lag, offsets e idempotência do sink | eventos podem atrasar ou duplicar. |
| 12 Streaming | consumer lag, checkpoint e watermark | stream exige controle de atraso e estado. |
| 13 ML fraude | point-in-time correctness e drift básico | features erradas geram modelo enganoso. |
| 14 IaC | plan/apply, idempotência e estado versionado | infra criada à mão não é reproduzível nem revisável. |
| 15 Qualidade | contratos de dados e validação na borda | fonte muda payload em silêncio e contamina dashboards. |
| 16 Observabilidade | freshness, volume e SLOs com alerta | job que falha sem erro serve dado velho ou incompleto. |

Segurança também entra progressivamente: variáveis em `.env`, separação de credenciais por serviço, usuários distintos por camada e cuidado para não commitar segredos reais. Como o projeto é local e didático, o foco é mostrar os controles essenciais sem transformar cada capítulo em uma stack de segurança completa.

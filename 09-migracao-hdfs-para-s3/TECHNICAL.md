# Complemento técnico — HDFS, S3 e migração de storage

## O que este capítulo aprofunda

Este capítulo trata de migracao de legado e engenharia de custo/performance. A pergunta não e "HDFS ou S3 do zero?", e sim: como migrar uma plataforma que já tinha HDFS para object storage sem quebrar consumidores?

## Pequena história

HDFS nasceu no ecossistema Hadoop nos anos 2000, inspirado por ideias de sistemas distribuidos como o Google File System. Ele foi criado para clusters em que storage e computacao ficavam juntos.

S3 foi lancado pela AWS em 2006 e mudou o desenho de data platforms. Em vez de manter discos nos mesmos servidores de computacao, empresas passaram a usar object storage elastico e separar compute de storage.

A industria migrou bastante de HDFS para S3 por custo operacional, elasticidade e separacao entre storage e compute. HDFS ainda aparece em ambientes on-prem, cargas de throughput alto, restricoes regulatórias, clusters legados e cenarios em que a empresa já pagou/operou a infraestrutura.

HDFS não e necessariamente "mais barato". Ele pode parecer barato quando a infraestrutura on-prem já existe, mas tem custo de operação, manutenção, capacidade ociosa e acoplamento com compute. S3/MinIO tende a ser mais elastico e simples para histórico frio e crescimento de storage.

## Por baixo dos panos do HDFS

HDFS divide arquivos em blocos grandes e replica esses blocos em datanodes. O namenode guarda metadados: onde cada bloco está, quais arquivos existem e qual o estado do cluster.

A ideia central e data locality. Se o dado está em um datanode, o motor de processamento tenta executar a tarefa perto dele, reduzindo tráfego de rede.

Esse desenho funciona bem para leituras sequenciais grandes, mas acopla storage e compute. Para aumentar storage, muitas vezes você também aumenta infraestrutura do cluster.

## Por baixo dos panos do S3

S3 e object storage. Objetos são acessados por chave e bucket. Ele desacopla storage de compute, escala muito bem e cobra conforme uso.

O tradeoff e latência de rede e semantica diferente de filesystem. Operações como rename atomico não são naturais. Por isso engines e formatos lakehouse precisam tratar commits com cuidado.

## Migracao e tiering

Tiering e a politica de mover dados entre camadas conforme valor de acesso. Em um cenario de migracao, ele também ajuda a decidir o que sai primeiro do HDFS.

No projeto:

- HDFS: legado on-prem e, temporariamente, zona quente para dados ainda muito acessados;
- S3/MinIO: alvo moderno da migracao e zona fria para histórico;
- Spark: motor que consulta as duas zonas.

Essa decisão não e apenas técnica. Ela mostra maturidade de plataforma: custo, SLA, legado e padrão de acesso definem arquitetura.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| AWS S3 Intelligent-Tiering | Tiering gerenciado por padrão de acesso. |
| Google Cloud Storage classes | Standard, Nearline, Coldline e Archive. |
| Azure Blob tiers | Hot, Cool, Cold e Archive. |
| Ceph | Storage distribuído open source com suporte a objeto. |
| Alluxio | Camada de cache e virtualizacao entre compute e storage. |

## Quando usar

Use storage hibrido quando ha padrões claros de acesso, diferenca relevante de custo/performance ou uma migracao real de legado que não pode acontecer em big bang.

Evite se o volume e pequeno ou se a operação do ambiente hibrido custa mais que a economia. Simplicidade também é uma decisão de engenharia.

## Como isso aparece no projeto

O capítulo 09 mostra que a evolucao para object storage raramente acontece em um ambiente vazio. A camada física de storage também precisa lidar com legado, migracao, custo, latência e continuidade operacional.

## 📚 Referências

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html) — object storage S3-compatible para desenvolvimento local e on-prem.
- [AWS S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/) — tiers de armazenamento da AWS com preços e latências.
- [Trino Hive Connector](https://trino.io/docs/current/connector/hive.html) — federação SQL sobre HDFS e S3 via metastore.

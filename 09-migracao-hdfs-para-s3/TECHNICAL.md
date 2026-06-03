# Complemento tecnico - HDFS, S3 e migracao de storage

## O que este capitulo aprofunda

Este capitulo trata de migracao de legado e engenharia de custo/performance. A pergunta nao e "HDFS ou S3 do zero?", e sim: como migrar uma plataforma que ja tinha HDFS para object storage sem quebrar consumidores?

## Pequena historia

HDFS nasceu no ecossistema Hadoop nos anos 2000, inspirado por ideias de sistemas distribuidos como o Google File System. Ele foi criado para clusters em que storage e computacao ficavam juntos.

S3 foi lancado pela AWS em 2006 e mudou o desenho de data platforms. Em vez de manter discos nos mesmos servidores de computacao, empresas passaram a usar object storage elastico e separar compute de storage.

A industria migrou bastante de HDFS para S3 por custo operacional, elasticidade e separacao entre storage e compute. HDFS ainda aparece em ambientes on-prem, cargas de throughput alto, restricoes regulatórias, clusters legados e cenarios em que a empresa ja pagou/operou a infraestrutura.

HDFS nao e necessariamente "mais barato". Ele pode parecer barato quando a infraestrutura on-prem ja existe, mas tem custo de operacao, manutencao, capacidade ociosa e acoplamento com compute. S3/MinIO tende a ser mais elastico e simples para historico frio e crescimento de storage.

## Por baixo dos panos do HDFS

HDFS divide arquivos em blocos grandes e replica esses blocos em datanodes. O namenode guarda metadados: onde cada bloco esta, quais arquivos existem e qual o estado do cluster.

A ideia central e data locality. Se o dado esta em um datanode, o motor de processamento tenta executar a tarefa perto dele, reduzindo trafego de rede.

Esse desenho funciona bem para leituras sequenciais grandes, mas acopla storage e compute. Para aumentar storage, muitas vezes voce tambem aumenta infraestrutura do cluster.

## Por baixo dos panos do S3

S3 e object storage. Objetos sao acessados por chave e bucket. Ele desacopla storage de compute, escala muito bem e cobra conforme uso.

O tradeoff e latencia de rede e semantica diferente de filesystem. Operacoes como rename atomico nao sao naturais. Por isso engines e formatos lakehouse precisam tratar commits com cuidado.

## Migracao e tiering

Tiering e a politica de mover dados entre camadas conforme valor de acesso. Em um cenario de migracao, ele tambem ajuda a decidir o que sai primeiro do HDFS.

No projeto:

- HDFS: legado on-prem e, temporariamente, zona quente para dados ainda muito acessados;
- S3/MinIO: alvo moderno da migracao e zona fria para historico;
- Spark: motor que consulta as duas zonas.

Essa decisao nao e apenas tecnica. Ela mostra maturidade de plataforma: custo, SLA, legado e padrao de acesso definem arquitetura.

## Tecnologias equivalentes

| Tecnologia | Comparacao |
| --- | --- |
| AWS S3 Intelligent-Tiering | Tiering gerenciado por padrao de acesso. |
| Google Cloud Storage classes | Standard, Nearline, Coldline e Archive. |
| Azure Blob tiers | Hot, Cool, Cold e Archive. |
| Ceph | Storage distribuido open source com suporte a objeto. |
| Alluxio | Camada de cache e virtualizacao entre compute e storage. |

## Quando usar

Use storage hibrido quando ha padroes claros de acesso, diferenca relevante de custo/performance ou uma migracao real de legado que nao pode acontecer em big bang.

Evite se o volume e pequeno ou se a operacao do ambiente hibrido custa mais que a economia. Simplicidade tambem e uma decisao de engenharia.

## Como isso aparece no projeto

O capitulo 09 mostra que a evolucao para object storage raramente acontece em um ambiente vazio. A camada fisica de storage tambem precisa lidar com legado, migracao, custo, latencia e continuidade operacional.

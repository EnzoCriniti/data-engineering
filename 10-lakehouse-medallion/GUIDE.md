# Cap. 10 — Lakehouse Medallion: Delta Lake sobre o data lake

> **Aula deste capítulo.** Aqui você aprende o *porquê* de cada conceito, com exemplos trabalhados e o raciocínio de design. O código completo e copiável está no **[SOLUTION.md](./SOLUTION.md)**; os internals das ferramentas (formato do log, comparação com Iceberg/Hudi, tuning) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

No capítulo 09 movemos o data lake para object storage (MinIO/S3): ganhamos escala e custo baixo. Mas um lake de arquivos soltos é **frágil**. Um exemplo concreto do que dá errado:

> Um job Spark começa a reescrever a tabela `entregas` (1.000 arquivos Parquet). Ele apaga 600, grava 350 novos e **falha** (estourou memória). A tabela agora tem 400 arquivos antigos + 350 novos = um estado que nunca existiu de verdade. Qualquer dashboard que ler nesse momento mostra números errados, e ninguém percebe.

Arquivos soltos no S3 não têm: **transação** (a escrita acima deveria ser tudo-ou-nada), **schema enforcement** (nada impede gravar uma coluna `preco` como texto em vez de número), **histórico** (não dá para voltar à versão de ontem), nem **upsert eficiente** (atualizar 1 linha exige reescrever o arquivo todo).

O **lakehouse** resolve isso: mantém os arquivos Parquet baratos do lake, mas adiciona um **log de transações** por cima que dá as garantias de um warehouse. Neste capítulo usamos **Delta Lake**.

## Pré-requisitos

- **Capítulo anterior:** 09 concluído (dados no MinIO/S3, Trino federando queries).
- **Conceitos que você já deve ter:** Parquet (cap 08), schema-on-read (cap 08), idempotência (caps 00, 04).
- **Docker:** versão 24+ com Docker Compose.

---

## Conceitos fundamentais

### 1. O que é um lakehouse — e por que ele existe

Antes existiam dois mundos separados:

| | Data Warehouse | Data Lake |
|---|---|---|
| Storage | caro, proprietário | barato, arquivos abertos (S3) |
| Garantias | ACID, schema, transações | nenhuma — "amontoado de arquivos" |
| Dados | só estruturado/tipado | qualquer formato |
| Risco | escala cara | virar *data swamp* (pântano de dados) |

O **lakehouse** é a tentativa de ter o melhor dos dois: **storage de lake + garantias de warehouse**. Não é um produto novo — é um *formato de tabela* (Delta Lake, Apache Iceberg, Apache Hudi) que se coloca por cima dos arquivos Parquet e adiciona um log transacional.

**O que está sendo usado neste capítulo:** Delta Lake, porque é o mais simples de demonstrar com Spark e o mais direto para mostrar ACID/time travel/MERGE. (Iceberg e Hudi resolvem o mesmo problema com trade-offs diferentes — ver TECHNICAL.)

### 2. Delta Lake: como ACID acontece sobre arquivos imutáveis

A pergunta-chave: *arquivos no S3 são imutáveis e não têm "transação" — como o Delta consegue ACID?*

A resposta é o **`_delta_log/`**. Uma tabela Delta não é só os Parquets; é os Parquets **+ um log de commits** ao lado:

```
s3a://datalake/silver/entregas/
├── _delta_log/
│   ├── 00000000000000000000.json   ← commit 0 (versão 0)
│   ├── 00000000000000000001.json   ← commit 1 (versão 1)
│   └── 00000000000000000002.json   ← commit 2 (versão 2 = atual)
├── part-0001.snappy.parquet
├── part-0002.snappy.parquet
└── part-0003.snappy.parquet
```

Cada arquivo de commit no log diz, em JSON, **quais Parquets entram e quais saem** naquela versão. Ao ler a tabela, a engine **não** lista os arquivos da pasta e assume que todos valem — ela lê o log e descobre quais Parquets compõem a versão atual.

**Exemplo trabalhado — voltando ao job que falhou no início:**

Com Delta, o job que reescreve a tabela não apaga nada no disco. Ele grava os 350 novos Parquets e só então tenta escrever **um** commit no log dizendo "remova estes 600, adicione estes 350". Se o job falha antes desse commit, o log nunca registrou a mudança → a leitura continua enxergando a versão anterior intacta. A escrita foi **atômica**: ou o commit existe (nova versão) ou não existe (versão velha). Nunca o estado-frankenstein.

Isso é o que destrava:

- **Commits atômicos** — uma escrita ou completa, ou é como se nunca tivesse acontecido.
- **Time travel** — `SELECT * FROM entregas VERSION AS OF 1` lê a versão 1, porque o log guarda o histórico de commits. Útil para auditoria e rollback.
- **Schema enforcement** — o log guarda o schema; uma escrita com tipo incompatível é rejeitada *antes* de corromper a tabela.
- **MERGE (upsert)** — atualizar/inserir por chave num único comando atômico. É a base do CDC do cap 11.
- **VACUUM** — remove fisicamente os Parquets antigos que nenhuma versão referencia mais (limpeza de custo).

### 3. Arquitetura Medallion — por que três camadas

Poderíamos jogar o dado cru direto numa tabela e transformar tudo numa query gigante. Por que separar em **bronze → silver → gold**?

Porque cada camada é um **contrato de qualidade** e isola um tipo de responsabilidade:

```mermaid
flowchart LR
    O[Origem: OLTP / API / eventos] -->|append, sem transformar| B[🥉 Bronze<br/>dado cru, fiel à origem]
    B -->|limpa, tipa, dedup, PII| S[🥈 Silver<br/>confiável e tratado]
    S -->|agrega, modela p/ negócio| G[🥇 Gold<br/>métricas prontas]
    G --> BI[BI / Meta
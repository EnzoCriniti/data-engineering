# Capítulo 17 — Capstone: a plataforma como um todo 🟢

> **De onde viemos:** dezessete capítulos depois, a NuvemStore saiu de um único banco OLTP para uma plataforma de dados completa — com warehouse, lake, lakehouse, streaming, CDC, base de ML, infra como código, qualidade e observabilidade. Cada capítulo nasceu de uma dor concreta do anterior. Este capítulo final não adiciona tecnologia nova: ele **amarra tudo numa história única, mostra a arquitetura consolidada e os resultados visíveis**.

## Por que um capstone

Os capítulos 00–16 formam uma trilha linear: cada um resolve uma dor e cria a próxima. Quem lê na ordem entende a evolução. Mas um recrutador passa 30 segundos no repositório — ele precisa, num só lugar, enxergar a plataforma inteira, entender as decisões e *ver* que funciona. É isso que o capstone entrega: a visão macro + a prova visual.

## A jornada inteira em uma página

| Fase | Capítulos | Dor que motivou | O que entrou |
| --- | --- | --- | --- |
| Fundação | 00–03 | "Onde o dado nasce e por que analytics não pode viver no OLTP?" | OLTP 3NF, modelagem dimensional, separação física do warehouse |
| Batch analytics | 04–06 | "Como mover e transformar dados de forma reproduzível e de múltiplas fontes?" | ELT com Python/DuckDB, dbt, ingestão de API externa |
| Operação | 07 | "Quem coordena, repete e recupera os jobs?" | Airflow (DAGs, retries, backfill) |
| Lake e migração | 08–09 | "E o histórico bruto e semi-estruturado que não cabe no warehouse?" | HDFS + Spark, migração para S3/MinIO com Trino federado |
| Lakehouse | 10 | "Como ter transação e time-travel sobre o lake?" | Delta Lake, Medallion (bronze/silver/gold) |
| Baixa latência | 11–12 | "Como refletir mudanças e métricas em tempo (quase) real?" | CDC com Debezium, streaming Kappa |
| Dados para ML | 13 | "Como servir um produto de ML com dados corretos?" | Feature table com point-in-time correctness |
| Produção | 14–16 | "Como isso vira produção: reproduzível, confiável e observável?" | IaC (Terraform/LocalStack), qualidade/contratos, observabilidade |
| Consolidação | 17 | "Como ver e provar a plataforma inteira?" | Este capstone |

## Arquitetura consolidada

```text
                    ┌─────────────────────────────────────────────────┐
   FONTES           │                  PLATAFORMA                       │   CONSUMO
                    │                                                   │
 OLTP (Postgres) ───┼─► CDC (Debezium) ─┐                              │
 API transportadora ┼─► ELT batch ──────┼─► Lake/Lakehouse ─► Gold ────┼─► BI (Metabase)
 GPS (streaming) ───┼─► Kappa ──────────┘   (Delta/Medallion)          ┼─► Feature table (ML)
                    │                                                   │
                    │   transversal: Airflow (orquestra) ·             │
                    │   Terraform (provisiona) · Qualidade (valida) ·  │
                    │   Observabilidade (freshness/volume/alerta)       │
                    └─────────────────────────────────────────────────┘
```

(O diagrama como código vive em [`diagrams/architecture.py`](./diagrams/architecture.py); o detalhamento macro está em [`../system-design`](../system-design).)

## O que demonstrar

O capstone é, sobretudo, uma **galeria de provas**. Para cada fase, há um resultado visível que comprova que aquilo roda — não só documentação. A lista do que capturar e como está no [GUIDE.md](./GUIDE.md); os prints ficam em [`assets/`](./assets/) e são referenciados no [RUNBOOK.md](./RUNBOOK.md).

## Decisões de plataforma (o "porquê" em uma olhada)

- **Problem-first, não tech-first.** Nenhuma ferramenta entrou por hype. Cada uma resolve uma dor nomeada — é a competência central que o repositório demonstra: julgamento de quando usar o quê.
- **Local e custo zero.** Tudo roda em Docker; a nuvem é emulada (LocalStack). O autor prova as competências sem expor-se a custos.
- **Idempotência em toda parte.** ELT, CDC, feature builder, IaC — todos reaplicáveis sem duplicar. É o fio condutor de confiabilidade.
- **Camadas com contrato.** Bronze append-only, silver deduplicada, gold derivada; contratos de qualidade na borda; SLOs observados. Cada camada tem uma garantia explícita.

## A dor que sobra (o roadmap honesto)

Nenhuma plataforma está "pronta". O que ainda aproximaria isto de um time pleno em produção:

- deploy contra uma nuvem real (substituindo o LocalStack), com CI rodando `terraform plan`;
- catálogo de dados com ownership e descrições;
- detecção automática de anomalias (além dos SLOs fixos);
- testes end-to-end dos pipelines no CI, não só validação de sintaxe;
- custo e performance por camada.

Reconhecer essas fronteiras faz parte da maturidade que o portfólio demonstra.

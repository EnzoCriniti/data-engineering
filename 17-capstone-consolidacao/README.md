# Capítulo 17 — Capstone: a plataforma como um todo

> **Status: documentado.** Este capítulo apresenta a arquitetura final planejada e reúne as evidências conforme cada fase é validada. A primeira execução batch está registrada no [diário da etapa 1](../docs/diario/etapa-1.md#provas).

## Por que um capstone

Os capítulos 00–16 formam uma trilha linear: cada um resolve uma dor e cria a próxima. Quem lê na ordem entende a evolução. Mas um recrutador passa 30 segundos no repositório — ele precisa, num só lugar, enxergar a plataforma inteira, entender as decisões e *ver* que funciona. É isso que o capstone entrega: a visão macro + a prova visual.

## A jornada inteira em uma página

| Fase | Capítulos | Pergunta da empresa | Evidência |
| --- | --- | --- | --- |
| Do checkout à receita diária | 00–04 | Quanto vendemos sem concentrar as consultas no banco da loja? | [Receita e contagens conciliadas](../docs/diario/etapa-1.md#provas) |
| Entregas com múltiplas fontes | 05–07 | Quais entregas terceirizadas estão atrasadas? | Indicador de SLA em uma carga reexecutável, planejado |
| Histórico de navegação | 08–10 | Onde os clientes abandonam a compra? | Funil consultável no lakehouse, planejado |
| Decisões durante o dia | 11–13 | O que mudou na frota e nos pagamentos? | Evento GPS e atualização de pagamento rastreados até o destino, planejados |
| Operação confiável | 14–17 | Como recuperar uma carga e identificar dados incorretos ou atrasados? | Recuperação, rejeição por contrato e alerta, planejados |

O [índice técnico](../docs/indice-tecnico.md) aponta para os guias de cada fase.

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

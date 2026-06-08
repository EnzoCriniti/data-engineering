# Capítulo 16 — Observabilidade do pipeline 🟡

> **De onde viemos:** a infra é reproduzível (cap 14) e o dado que entra é validado (cap 15). Mas a operação ainda é cega ao *processo*: se um job do Airflow falha às 3h da manhã, se uma tabela para de ser atualizada, ou se um pipeline que costumava processar 50 mil linhas processa 12, ninguém fica sabendo até um humano reclamar de um número estranho.

## Cenário de negócio

O time da NuvemStore descobriu, numa segunda-feira, que o mart de receita estava com os números de sexta: o job de carga do fim de semana falhou silenciosamente e o dashboard simplesmente serviu dados velhos sem avisar. A decisão da manhã foi tomada com dado defasado.

A lição: validar o dado (cap 15) não basta — é preciso observar o **processo**. Os dados estão *frescos*? O volume está dentro do normal? O job rodou? Observabilidade responde a essas perguntas e dispara alerta quando a resposta é "não", antes do humano perceber.

## O que esta etapa mostra

A coleta de **sinais de saúde** sobre as tabelas e jobs da plataforma — freshness (quão velho é o dado mais recente), volume (quantas linhas no último lote vs o esperado), e status de execução — com regras que disparam alerta quando um sinal sai da faixa normal.

```text
tabelas/jobs  ->  coletor de métricas  ->  [freshness? volume? rodou?]
                                                |
                                                fora do normal -> alerta
```

## Conceitos

**Os três pilares (adaptados a dados).** Observabilidade clássica fala de métricas, logs e traces. Em dados, o que importa é: **freshness** (o dado está atualizado?), **volume** (a quantidade está normal?), **schema** (a estrutura mudou? — coberto no cap 15), **distribuição** (os valores estão dentro do padrão?) e **lineage** (o que depende do quê?).

**Freshness.** A diferença entre agora e o timestamp do registro mais recente de uma tabela. Um mart que deveria atualizar a cada hora e está com 9 horas de atraso é um incidente — mesmo que cada linha individual seja válida.

**Volume / anomalia de volume.** O número de linhas do último lote comparado ao histórico. Cair de 50 mil para 12 linhas, sem erro explícito, é o sintoma de um job meio-quebrado.

**SLA / SLO de dados.** Um acordo de nível de serviço sobre os dados: "o mart de receita está fresco em até 2h, 99% dos dias". O alerta dispara quando o SLO é violado.

**Alerta acionável vs ruído.** Um bom alerta diz *o que* quebrou, *onde* e *o quão grave* — e só dispara quando há ação a tomar. Alerta demais treina o time a ignorar (alert fatigue); o desafio é calibrar.

**Lineage.** O mapa de dependências entre fontes, jobs e tabelas. Quando o mart de receita está defasado, o lineage mostra que a causa-raiz é o job de ingestão do OLTP que falhou três passos atrás.

> Detalhamento técnico (Prometheus/Grafana, Elementary/Monte Carlo, métricas push vs pull) em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base / documentação.** O compose sobe um coletor que mede freshness e volume das tabelas **gold do lakehouse** (cap 10/12) via **Trino** e avalia regras de SLO. O roteiro está no [GUIDE.md](./GUIDE.md) e o código no [SOLUTION.md](./SOLUTION.md).

- **[RUNBOOK.md](./RUNBOOK.md)** — rodar o coletor, ver as métricas e disparar um alerta de teste (com espaço para prints).

## A dor que sobra

Com infra reproduzível, dado validado e processo observado, a plataforma cobre os controles essenciais de produção. O que falta não é uma tecnologia nova — é **amarrar tudo numa história única e demonstrável**: a arquitetura consolidada, a plataforma rodando ponta-a-ponta, e os resultados visíveis. Esse é o papel do capítulo final: o **capstone**.

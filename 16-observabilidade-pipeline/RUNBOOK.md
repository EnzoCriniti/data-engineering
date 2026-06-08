# Runbook — Capítulo 16: observabilidade do pipeline

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — o coletor sobe pronto; os SLOs e as regras de alerta são o roteiro do [GUIDE.md](./GUIDE.md) (código no [SOLUTION.md](./SOLUTION.md)).

## O que este capítulo entrega hoje

Um coletor que mede freshness (quão velho é o dado) e volume (quantas linhas vs o esperado) das tabelas **gold do lakehouse**, compara com SLOs declarados e dispara alerta quando um sinal sai do normal.

## Pré-requisitos

- Docker e Docker Compose.
- O ambiente do capítulo 10 (lakehouse) no ar, com o gold materializado e o Trino acessível. O coletor conecta ao Trino pela rede do compose do cap 10 — ligue os dois ambientes na mesma rede (ver abaixo).

## Subir e rodar

```bash
cp .env.example .env
docker compose --profile jobs run --rm observability
```

## Validar

Esperado: relatório com freshness e volume por tabela, todos ✅, e exit 0 quando tudo está dentro dos SLOs.

Para provar o alerta, simule um incidente: ajuste `max_freshness_hours` para `0` em `observability/slos.json` (ou deixe o streaming do cap 12 parado para a gold de velocidade envelhecer) e rode de novo. O coletor marca ❌, imprime `ALERTA` e sai com código 1 — o que pararia a DAG do Airflow e dispararia notificação em produção.

## Prints da execução

> Salve as capturas em [`assets/`](./assets/) conforme resolver o capítulo.

Sugestões do que capturar:

- Relatório do coletor com tudo dentro dos SLOs — `assets/16-slos-ok.png`
- Relatório com SLO violado (`ALERTA`) — `assets/16-alerta.png`
- Se montar Prometheus/Grafana: o painel de freshness/volume — `assets/16-grafana.png`

<!--
![SLOs ok](./assets/16-slos-ok.png)
![alerta](./assets/16-alerta.png)
-->

## Recomeçar do zero

```bash
docker compose down -v
```

## Próximo passo

[Capítulo 17](../17-capstone-consolidacao): o capstone — amarrar toda a plataforma numa história única, com a arquitetura consolidada e os resultados demonstrados.

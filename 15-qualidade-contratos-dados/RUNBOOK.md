# Runbook — Capítulo 15: qualidade e contratos de dados

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — o runner de qualidade sobe pronto; as suítes de expectativas e o checkpoint são o roteiro do [GUIDE.md](./GUIDE.md) (código no [SOLUTION.md](./SOLUTION.md)).

## O que este capítulo entrega hoje

Um portão de qualidade que valida as tabelas gold do lakehouse (`resumo_entregas`, `velocidade_regional`) contra contratos declarados, falhando alto quando uma regra de negócio é violada — antes do número chegar ao BI/feature table.

## Pré-requisitos

- Docker e Docker Compose.
- O ambiente do capítulo 10 (lakehouse) no ar, com o gold materializado e o Trino acessível. O runner deste capítulo conecta ao Trino pela rede do compose do cap 10 — ligue os dois ambientes na mesma rede (ver abaixo).

## Subir e rodar

```bash
cp .env.example .env
docker compose --profile jobs run --rm quality
```

## Validar

Esperado: log `PORTÃO ABERTO: todos os contratos passaram.` e exit 0 quando os dados estão sanos.

Para provar que o portão funciona, aponte para um gold com `velocidade_media` acima de 200 (simulando leitura de GPS corrompida) e rode de novo: o runner aponta a violação e sai com código 1.

## Prints da execução

> Salve as capturas em [`assets/`](./assets/) conforme resolver o capítulo.

Sugestões do que capturar:

- Log do portão passando (`PORTÃO ABERTO`) — `assets/15-portao-aberto.png`
- Log do portão barrando dado ruim (`PORTÃO FECHADO`, com a linha apontada) — `assets/15-portao-fechado.png`
- Data docs / relatório de qualidade, se gerar via Great Expectations — `assets/15-data-docs.png`

<!--
![portão aberto](./assets/15-portao-aberto.png)
![portão fechado](./assets/15-portao-fechado.png)
-->

## Recomeçar do zero

```bash
docker compose down -v
```

## Próximo passo

[Capítulo 16](../16-observabilidade-pipeline): tornar a operação visível — métricas, freshness e alertas de falha.

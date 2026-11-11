# 0003 — Capítulos isolados para estudo, ambiente vivo cumulativo no NAS

- **Status:** Aceita
- **Data:** 10/11/2026

## Contexto

O repositório foi pensado para rodar um capítulo por vez, cada um com seu `docker-compose.yml`, recriando o estado final do capítulo anterior. Isso é ótimo para estudar, mas não descreve uma plataforma real, em que as camadas convivem e evoluem sem desligar tudo a cada mudança. Publicar 18 composes separados no NAS também não faria sentido.

## Decisão

Manter os dois modos:

- **Modo estudo:** cada capítulo continua com o próprio compose e roda sozinho, como hoje.
- **Modo vivo:** um único compose em `deploy/nas/docker-compose.yml` que cresce a cada etapa e representa a plataforma da NuvemStore em operação. Ele reaproveita as mesmas imagens e scripts dos capítulos (seeder, pipeline, modelos dbt, DAGs), sem duplicar código.

Quando a história diz que uma camada virou legado (ex.: o warehouse Postgres depois do lakehouse), o modo vivo faz a migração validada e desliga o serviço antigo numa etapa explícita, como numa empresa de verdade.

## Alternativas consideradas

- **Publicar o compose do capítulo mais recente:** perderia as camadas anteriores e os dados acumulados.
- **Só o modo vivo:** quebraria a proposta didática de rodar um capítulo isolado.

## Consequências

- Os jobs precisam ser parametrizáveis por ambiente (URLs e caminhos por variável), para servir aos dois modos.
- O modo vivo precisa de um simulador de pedidos diário, que não existe no modo estudo.
- A memória do NAS limita o que fica ligado ao mesmo tempo; serviços pesados rodam sob demanda.

# 0002 — Ambiente vivo publicado pelo agent-platform

- **Status:** Aceita
- **Data:** 10/11/2026

## Contexto

Quero a plataforma de dados rodando de verdade no meu NAS, e não só na máquina de quem clona o repositório. O NAS já tem Dokploy, Forgejo, Traefik e Cloudflare Tunnel, e o agent-platform, a plataforma que construí, publica projetos nele com staging, aprovação humana e produção.

Em 10/11/2026 o agent-platform publicava apenas um container web por projeto (tipos `static` e `nixpacks`). Não havia suporte a Compose, volumes persistentes, secrets por ambiente nem jobs, que são justamente o que um projeto de dados precisa (ver `docs/control-plane.md` §5.4 no agent-platform).

## Decisão

Publicar o ambiente vivo pelo agent-platform, e para isso **estender a plataforma** com suporte a projetos Compose: manifesto declarado no repositório, secrets no cofre, volumes protegidos, limites de recurso obrigatórios, jobs one-shot pela interface, rotas por serviço e linha do tempo das etapas. O pedido completo está em [anexos/pedido-agent-platform.md](../anexos/pedido-agent-platform.md).

## Alternativas consideradas

- **Projeto Compose direto no Dokploy, fora da plataforma:** funciona hoje, mas deixa o projeto de dados fora da tela onde gerencio todos os outros e perde a história de uma plataforma publicando a outra.
- **Rodar só localmente:** mais simples, mas sem ambiente vivo não há dados novos todo dia, dashboard público ou prova de operação.

## Consequências

- O deploy de cada etapa depende da plataforma estar pronta. O código e o CI de cada etapa não dependem, então o trabalho no repositório de dados segue em paralelo.
- O agent-platform passa a suportar projetos com estado, o que melhora a plataforma para outros projetos também.
- O repositório precisa seguir o contrato descrito em [deploy-nas-agent-platform.md](../deploy-nas-agent-platform.md).

# Diário da etapa 1 — Fundação batch

> Capítulos 00, 02, 03 e 04. Branch `etapa-1`. Plano em [plano-de-implementacao.md](../plano-de-implementacao.md#etapa-1-em-detalhe).

## 10/11/2026

### Diagnóstico do ponto de partida

- O repositório tinha 18 capítulos documentados (README, GUIDE, SOLUTION, RUNBOOK, TECHNICAL), o `COMPANY.md`, o `system-design/`, os modelos DBML e o CI.
- Não havia nenhum arquivo executável: o commit `85d04b1` tinha movido todo o código para dentro dos `SOLUTION.md`.
- O README marcava os capítulos 00, 03, 04 e 17 como "Integração implementada".
- Os `.env.example` dos capítulos 02, 03 e 04 usavam nomes de variáveis diferentes dos composes das soluções (ex.: `DB_USER`/`DB_PASSWORD` no `.env.example` contra `PG_USER`/`PG_PASS` no compose). O RUNBOOK do capítulo 00 manda subir um serviço `db`, mas o serviço se chama `postgres`.

### Decisões do dia

- [0001](../decisoes/0001-codigo-real-na-main.md) código real na `main`.
- [0002](../decisoes/0002-deploy-pelo-agent-platform.md) ambiente vivo pelo agent-platform, que vai ganhar suporte a Compose.
- [0003](../decisoes/0003-ambiente-vivo-cumulativo.md) capítulos isolados + ambiente vivo cumulativo.
- [0004](../decisoes/0004-trilha-sem-solucoes-gerada.md) trilha sem soluções gerada por script.

### Feito

- Código dos capítulos 00, 02, 03 e 04 extraído dos `SOLUTION.md` para arquivos reais, por script (cada bloco sob um título `` ## `caminho` `` virou o arquivo correspondente).
- `.env.example` dos capítulos 02, 03 e 04 alinhados com os composes.
- Documentação do projeto criada em `docs/`.
- Pedido de suporte a projetos de dados enviado para o agent-platform.

### Pendente

- [ ] Rodar cada capítulo localmente (bloqueado: Docker Desktop não iniciou nesta sessão).
- [x] Alinhar os RUNBOOKs dos capítulos 00, 02, 03 e 04 com serviços, portas e consultas do código.
- [x] Converter os `SOLUTION.md` dos capítulos 00, 02, 03 e 04 para o novo formato.
- [x] Confirmar a primeira execução do teste de ponta a ponta no GitHub Actions.
- [x] Corrigir os status do README raiz.
- [x] `deploy/nas/` com simulador diário e agendador.
- [ ] Trilha sem soluções (script, `exercicio.yml`, workflow).
- [ ] Publicar no NAS (depende do agent-platform).
- [ ] Texto do portfólio.

## Provas

Primeira validação via SSH em um ambiente temporário com PostgreSQL 16.15, Python 3.11 e DuckDB 1.1.0. O Compose foi validado em separado com `docker compose config`. A execução posterior em containers está registrada abaixo.

| Capítulos | Validação | Resultado |
| --- | --- | --- |
| 00 e 02 | Aplicar os schemas e rodar o seeder | 4 tabelas no schema analítico, 250 clientes e 1.200 pedidos na origem |
| 03 | Migrar do OLTP para um banco de warehouse separado no mesmo servidor de teste | 3.188 itens e a mesma receita nos dois bancos |
| 04 | Rodar o ELT duas vezes sobre a mesma origem e conferir o DuckDB | 8 tabelas com contagens iguais, 1.033 pedidos não cancelados, receita de R$ 1.668.388,10 na origem e no mart, e 20 produtos no ranking em ambas as execuções |

## 11/11/2026

- README e capstone reorganizados em cinco fases. Os 18 capítulos ficaram no [índice técnico](../indice-tecnico.md).
- O [job de ponta a ponta](../../.github/workflows/ci.yml) sobe o Compose do capítulo 04, carrega a origem e executa o ELT duas vezes. O [verificador](../../04-elt-batch-com-python/pipeline/verify.py) confere as tabelas raw, a quantidade de pedidos e a receita por dia.
- O novo verificador passou nas duas execuções via SSH com o PostgreSQL temporário. Ambas retornaram 8 tabelas raw conciliadas, 1.033 pedidos, receita de R$ 1.668.388,10 e 20 produtos no ranking. Uma alteração deliberada na receita do DuckDB foi detectada.
- Os gabaritos agora explicam as decisões e apontam para os arquivos executáveis e as validações. O seeder usa os IDs retornados pelo PostgreSQL, inclusive quando uma tentativa interrompida já consumiu IDs. O ELT lê um snapshot da origem e publica as tabelas em uma transação DuckDB.
- O [manifesto](../../.platform/app.json) e o [Compose do NAS](../../deploy/nas/docker-compose.yml) passaram no validador do Agent Platform sem avisos e no `docker compose config --profile jobs` com e sem overlay. O validador calculou 1.152 MiB para staging e 1.536 MiB para produção, incluindo o maior job. São limites configurados.
- O ambiente cumulativo usa volumes nomeados, rede interna e DDL nas imagens. O seeder faz bootstrap apenas em banco vazio. O simulador grava pedidos e o marcador do dia na mesma transação. O agendador executa o simulador e as duas cargas às 06:00 UTC. Um lock compartilhado no volume DuckDB serializa os jobs manuais e agendados.
- O desktop respondeu via SSH e segue sem Docker ou Podman. O daemon Docker do notebook estava indisponível. Os containers foram executados em runners isolados do GitHub Actions.
- O control plane publicado respondeu em `/api/health` e o arquivo de versão no NAS retornou `47af4ba`, que contém o fluxo Compose. A chave Forgejo autenticou, mas o repositório `Enzo/data-engineering` não estava acessível por ela. A [PR #1](https://github.com/EnzoCriniti/data-engineering/pull/1) foi aberta em rascunho no GitHub usando a credencial do Git, com acesso à API via SSH ao desktop.

| Job no GitHub Actions | Resultado no commit `4de30c1` |
| --- | --- |
| [Capítulo 04](https://github.com/EnzoCriniti/data-engineering/actions/runs/42952306746/job/130299202405) | 1.200 pedidos na origem. As duas execuções conciliaram 8 tabelas raw, 1.033 pedidos não cancelados e R$ 1.668.388,10 de receita. |
| [Compose cumulativo com overlay de staging](https://github.com/EnzoCriniti/data-engineering/actions/runs/42952306746/job/130299202474) | Bootstrap repetido, 205 pedidos após acrescentar um único lote de cinco, 541 itens e R$ 289.859,60 conciliados no warehouse. O DuckDB conciliou 8 tabelas raw e 181 pedidos não cancelados. Depois de parar e recriar os containers, os dois bancos PostgreSQL conservaram as contagens e o DuckDB passou na verificação antes de uma nova carga. |

## Próxima sessão

Revisar a PR. Importar ou liberar acesso à NuvemStore no Forgejo, vincular o repositório ao Agent Platform e cadastrar as duas senhas de staging no cofre. Seguir o [aceite do primeiro staging](../deploy-nas-agent-platform.md#aceite-do-primeiro-staging), incluindo o teste de parada e redeploy pelo Dokploy e a medição de memória. A revisão e o aceite de staging antecedem a tag e a aprovação de produção.

## O que aprendi

Preencher ao fechar a etapa.

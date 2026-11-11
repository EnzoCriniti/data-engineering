# Deploy no NAS pelo agent-platform

> O ambiente vivo da NuvemStore é publicado pelo [agent-platform](https://github.com/EnzoCriniti/agent-platform-public), a plataforma que construí para desenvolver e publicar meus projetos com agentes de IA. Este documento é o contrato entre os dois projetos.

## Por que pela minha plataforma

O agent-platform já faz, para apps web, o caminho completo: código no Forgejo, build no Dokploy, staging protegido, aprovação humana e produção com a mesma imagem. Usar a mesma plataforma para o projeto de dados dá duas coisas:

- **gestão em um lugar só:** vejo as etapas, os serviços, os logs e as releases do projeto de dados na mesma tela dos outros projetos;
- **uma história só no portfólio:** a plataforma de dados é publicada pela plataforma de agentes que eu mesmo construí.

Até 10/11/2026 a plataforma publicava só um container web por projeto (`static` ou `nixpacks`), sem volumes, secrets ou jobs. O suporte a projetos Compose foi pedido como trabalho no próprio agent-platform. Ver [decisão 0002](./decisoes/0002-deploy-pelo-agent-platform.md).

## Validação em 11/11/2026

- O checkout `feat/projetos-compose` já implementa manifesto, validação, variáveis por ambiente, limites, deploy por etapa, jobs e aba Etapas. Os 48 testes direcionados de Compose e interface passaram.
- O arquivo `source/.versao-publicada` no NAS identifica o commit `47af4ba`, descendente de `0dce30f`, que introduziu o fluxo Compose. A NuvemStore foi importada no Forgejo, vinculada à plataforma e publicada em staging pelo Dokploy.
- O [Compose do NAS](../deploy/nas/docker-compose.yml) passou no validador do checkout irmão e no `docker compose config` com e sem o overlay. As imagens incluem o DDL e cada ambiente usa volumes próprios para os dois bancos PostgreSQL e o DuckDB.
- A aba Etapas permite desligar o ambiente inteiro de staging e voltar a ligá-lo no próximo deploy. O teste no NAS preservou os três volumes e os totais conciliados. Para retirar um serviço específico de produção, planeje a mudança em uma release e verifique a recuperação dos dados antes da alteração. [Evidências da etapa](./diario/etapa-1.md#aceite-no-nas)

## O que a plataforma precisa oferecer

Pré-requisitos para publicar a etapa 1. Marque conforme a plataforma for entregando.

- [ ] Tipo de projeto `compose`, declarado em `.platform/app.json`.
- [ ] Variáveis e secrets por ambiente, guardados no cofre e checados contra o `.env.example`.
- [ ] Volumes persistentes que nunca são apagados por redeploy, rollback ou remoção.
- [ ] Validação de `mem_limit` e `cpus` em todo serviço, com orçamento visível.
- [ ] Fluxo de release para projeto com estado (staging leve ou opcional, produção pelo commit aprovado).
- [ ] Jobs one-shot (`profiles: [jobs]`) disparáveis pela interface, com logs e código de saída.
- [ ] Rota por serviço em `*.pescicloud.com` (necessária a partir da etapa 2, para o Metabase).
- [ ] Linha do tempo das releases ligada às tags `etapa-N`.
- [ ] Origem no Forgejo com espelho para o GitHub.

O pedido completo para a plataforma está em [anexos/pedido-agent-platform.md](./anexos/pedido-agent-platform.md).

## Como este repositório se apresenta para a plataforma

### Manifesto (`.platform/app.json`)

```json
{
  "type": "compose",
  "composePath": "deploy/nas/docker-compose.yml",
  "envExamplePath": "deploy/nas/.env.example",
  "staging": { "mode": "overlay", "overlayPath": "deploy/nas/docker-compose.staging.yml" },
  "services": {}
}
```

A partir da etapa 2, `services` ganha as rotas, por exemplo `"metabase": { "port": 3000, "route": true }`. O formato final segue o que for implementado no agent-platform; se mudar, este documento e o manifesto mudam juntos.

### Ambiente vivo (`deploy/nas/`)

```text
deploy/nas/
├── docker-compose.yml          # o ambiente cumulativo, cresce a cada etapa
├── docker-compose.staging.yml  # overlay de staging: menos dados, limites menores
├── .env.example                # chaves obrigatórias (valores reais ficam no cofre da plataforma)
├── postgres.Dockerfile        # inclui o DDL de cada banco na imagem
├── jobs.Dockerfile            # compartilha o código dos capítulos com os jobs
└── jobs/                      # bootstrap, simulador e agendamento
```

Regras do compose do NAS (além do [padrão geral](./padrao-do-repositorio.md#docker-compose)):

- todo serviço com `mem_limit` e `cpus`;
- volumes nomeados sem `name:` fixo ou `external`. Para persistir dados em bind, usar um caminho sob `${AP_DATA_DIR}`, injetado pela plataforma por ambiente;
- sem `container_name`, `ports`, `network_mode: host`, `privileged` ou `docker.sock`: a plataforma recusa o deploy;
- Postgres e demais serviços com estado sem rota pública;
- o agendador Python da fundação executava às 06:00 UTC (03:00 em São Paulo). O Compose de entregas transfere esse horário para o DAG Airflow. Os jobs manuais usam o perfil `jobs`. [Aceite da fase de entregas](./diario/fase-2-entregas.md#aceite-no-nas);
- serviços que viram legado na história (ex.: o warehouse Postgres depois do lakehouse) são desligados numa etapa explícita, com a migração validada antes.

### Origem do código

O repositório público no GitHub é a vitrine. A plataforma escuta o Forgejo do NAS. O caminho combinado:

1. o repositório é importado no Forgejo pela plataforma e passa a ser a origem;
2. o Forgejo espelha para o GitHub a cada push (push mirror);
3. o CI do GitHub continua rodando nas PRs e na `main`.

## Fluxo de uma etapa até o NAS

1. A PR da etapa `etapa-N` é revisada e mesclada.
2. O push na branch `staging` do Forgejo publica staging. Antes disso, a plataforma valida o manifesto, os limites, os volumes e os secrets.
3. Staging sobe com o overlay leve. Os jobs da etapa rodam pela interface e os resultados ficam nos logs.
4. A tag `etapa-N`, num commit que já está em staging, abre a aprovação de produção. A release recebe o rótulo `etapa-N` na linha do tempo.
5. Eu aprovo. Produção sobe a partir do commit da tag (conferido pelo SHA), com as imagens de terceiros fixadas pelo digest visto em staging. A plataforma mostra se o digest de algum serviço divergiu entre staging e produção. Reaproveitar as imagens construídas em staging fica para uma versão seguinte da plataforma.
6. As provas (prints da plataforma, saídas dos jobs, consumo de memória) vão para o diário da etapa.

## Aceite do primeiro staging

1. Cadastre `OLTP_PASSWORD` e `WAREHOUSE_PASSWORD` em **Etapas → Variáveis e segredos** de staging e confira o teto de memória. Os valores ficam no cofre.
2. Depois do deploy, rode `seeder` e confira 50 clientes e 200 pedidos. A segunda execução deve informar que o OLTP já foi populado. O bootstrap do NAS só escreve no OLTP vazio. O seeder de estudo com reset fica reservado ao ambiente descartável.
3. Rode `pipeline` e confira a migração do PostgreSQL e a reconciliação do DuckDB. Rode `simulador` duas vezes no mesmo dia UTC. O primeiro lote do dia acrescenta cinco pedidos em staging e as repetições não acrescentam pedidos. O agendador pode ter rodado o primeiro lote.
4. Confira os logs do próximo lote agendado. O lote atualiza o warehouse PostgreSQL e o DuckDB após gerar os pedidos.
5. Registre a contagem de pedidos, a contagem e a receita da fato e o resultado do DuckDB. Desligue staging na aba **Etapas**, faça o próximo deploy de staging e confira os três volumes antes de rodar uma nova carga. Se o redeploy cruzar a janela diária, use o registro de simulação para explicar a diferença.

## Orçamento de memória por etapa

Os valores estimados estão no [plano](./plano-de-implementacao.md#etapas). Depois de cada publicação, anote aqui o consumo medido.

| Etapa | Serviços residentes | Limite somado | Pico medido |
|---|---|---|---|
| 1 — staging | oltp, warehouse, agendador | 832 MiB residentes, 1.152 MiB com um job | a medir |
| 1 — produção | oltp, warehouse, agendador | 1.152 MiB residentes, 1.536 MiB com um job | a medir |

Uma amostra após a primeira carga de staging registrou 73,3 MiB residentes nos três serviços.

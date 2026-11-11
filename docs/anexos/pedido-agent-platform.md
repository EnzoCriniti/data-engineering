# Pedido ao agent-platform: suporte a projetos de dados

> Texto enviado em 10/11/2026 para a sessão de trabalho no repositório agent-platform. Guardado aqui como registro da história.

Quero que o agent-platform passe a publicar e gerenciar **projetos de dados multi-serviço**, não só apps web de um container. O primeiro cliente é o meu portfólio `EnzoCriniti/data-engineering` (trilha "NuvemStore"), que vai crescer em etapas no NAS: etapa 1 com Postgres OLTP + seeder + job de ELT (Python/DuckDB); depois dbt + Metabase, Airflow, MinIO/Spark/Trino, Redpanda/Debezium. Cada etapa vira uma tag `etapa-N` e é publicada a partir de um compose cumulativo em `deploy/nas/docker-compose.yml` no repo do projeto. Quero usar a plataforma para **visualizar e gerenciar essas etapas**, e essa integração vai ser contada como parte da história do portfólio, então tudo precisa ficar documentado.

## Limites atuais (confirme no código antes de mudar)

- `apps/control-plane/src/dokploy.ts` (`buildTypePara`) só gera `static` ou `nixpacks`: um projeto = uma Application com uma porta.
- `docs/control-plane.md` §5.4: não há configuração por projeto para volumes, bancos, secrets de ambiente, redes ou portas.
- `.platform/app.json` só tem `port`.
- O fluxo de release promove a mesma imagem por digest de staging para produção, pensado para app sem estado.
- O único cron é o dos revisores (`review-scheduler.ts`).

## O que precisa existir

1. **Tipo de projeto `compose`**, declarado no repo (não inferido da stack). Estender `.platform/app.json`, por exemplo:
   `{ "type": "compose", "composePath": "deploy/nas/docker-compose.yml", "services": { "metabase": { "port": 3000, "route": true } } }`.
   Publicar via API de Compose do Dokploy (verificar os endpoints reais da versão instalada), com o mesmo scaffold de staging e produção que já existe para Applications. Projetos `static`/`nixpacks` continuam funcionando sem mudança.

2. **Variáveis e secrets por ambiente**, guardados no cofre do control plane e injetados no compose pelo Dokploy. Usar o `.env.example` do repo como lista de chaves obrigatórias: o deploy é bloqueado se faltar alguma. Valores nunca aparecem em logs, eventos, UI de leitura ou no repo. Tela para cadastrar/editar por ambiente.

3. **Volumes persistentes e seguros.** Só volumes nomeados ou caminhos sob `/volume2/docker/<projeto>/<ambiente>/`. Rejeitar bind mount fora disso e caminhos em pastas criptografadas. Redeploy, rollback e remoção de projeto **nunca** apagam volume; apagar dado só por ação humana explícita e auditada.

4. **Orçamento de recursos.** Validar antes do deploy que todo serviço tem `mem_limit` e `cpus` (regra já na SPEC). Mostrar a soma por projeto/ambiente contra a RAM livre do NAS (22 GB, compartilhados com Forgejo, Dokploy e control plane) e bloquear ou avisar quando passar de um limite configurável.

5. **Release para projeto com estado.**
   - Staging leve e opcional por projeto: overlay `docker-compose.staging.yml` (menos dados, limites menores) ou a opção de pular staging para projetos de dados.
   - Produção promovida pelo commit/tag aprovado, registrando os digests das imagens de cada serviço construído em staging e reutilizando-os quando possível.
   - Aprovação humana para produção continua obrigatória.
   - Postgres e outros serviços de estado nunca expostos publicamente; sem publicação de porta no host por padrão (rede interna do compose).

6. **Jobs one-shot.** Serviços com `profiles: [jobs]` (ex.: `seeder`, `pipeline`) aparecem como ações "Executar" na UI, com logs da execução, duração e código de saída. O agendamento fica dentro do próprio compose (container de cron); a plataforma só mostra a última execução e o status, se der para obter dos logs/containers.

7. **Rotas por serviço.** Domínio por serviço do compose (o Dokploy aceita domínio com `serviceName`), subdomínio direto do wildcard `*.pescicloud.com`, staging com o basic auth que já existe, produção dentro da aprovação, como hoje.

8. **Visualização de etapas.** Na página do projeto: linha do tempo das releases ligada às tags `etapa-N` (data, commit, serviços incluídos, status, quem aprovou), serviços com health/estado/limites, logs por serviço e links das rotas. É o que vou usar para gerenciar e mostrar a evolução.

9. **Origem do código.** O repo é público no GitHub, e a plataforma escuta o Forgejo. Suportar o caminho recomendado: importar o repo para o Forgejo como origem, com push mirror para o GitHub (que continua sendo a vitrine pública). Documentar o passo a passo.

## Fora de escopo

Gerência geral de redes Docker, DNS/Cloudflare, Tailscale; suporte específico a Airflow/Spark (são só serviços do compose); backup automático (registrar como próximo passo).

## Critérios de aceite

- Um projeto de teste com compose (Postgres + job one-shot + um web simples com rota) sobe em staging e produção pelo fluxo normal da plataforma.
- Os dados do Postgres sobrevivem a redeploy, rollback e promoção.
- Remover o projeto não apaga volumes.
- Secret ausente bloqueia o deploy com mensagem clara; valores não aparecem em lugar nenhum.
- Serviço sem `mem_limit`/`cpus` é rejeitado.
- O job one-shot pode ser disparado pela UI e mostra logs e código de saída.
- Testes automatizados para validação do manifesto, volumes, limites e secrets.
- Documentação atualizada: `ESTADO.md`, `docs/control-plane.md` §5.4, `docs/roadmap-produto.md`, `SPEC.md` (manifesto), mais um registro de decisão explicando por que a plataforma passou a suportar projetos com estado, e um guia curto "como publicar um projeto compose".

## Restrições

- Nada apaga volumes, discos, repositórios ou dados já existentes no NAS.
- Trabalhar em branch e PR no Forgejo; nada vai para `main` sem meu OK. Commitar só quando eu pedir.
- Documentação em português (pt-BR).
- Antes de implementar, me mostre um plano curto com o que muda em cada arquivo e as decisões em aberto (principalmente o item 5).

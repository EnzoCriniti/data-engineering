# Plano de implementação

> Estado em 10/11/2026. Atualize a tabela de etapas ao fim de cada etapa e registre o detalhe no [diário](./diario/).

## Ponto de partida

O repositório nasceu com código nos primeiros capítulos e depois foi reorganizado como uma trilha de estudo: cada capítulo ganhou `GUIDE.md` (a aula) e `SOLUTION.md` (o gabarito), e o código saiu dos arquivos e ficou só dentro dos `SOLUTION.md` (commit `85d04b1`). O resultado foi uma documentação forte, com 18 capítulos, mas **nenhum arquivo executável**. O README ainda marcava capítulos como "Integração implementada", o que não era verdade.

Este plano transforma a documentação em uma plataforma que roda de verdade, em etapas, e que fica **no ar no meu NAS** desde a primeira etapa.

## Princípios

1. **Código real na `main`.** Quem abre o repositório vê arquivos que rodam, não código dentro de Markdown. Ver [decisão 0001](./decisoes/0001-codigo-real-na-main.md).
2. **Status honesto.** Um capítulo só é marcado como implementado quando roda localmente e passa no teste de ponta a ponta do CI.
3. **Dois modos de execução.** Cada capítulo continua rodando sozinho na máquina de quem estuda (o compose do capítulo). Em paralelo, existe um **ambiente vivo cumulativo** no NAS, que cresce a cada etapa. Ver [decisão 0003](./decisoes/0003-ambiente-vivo-cumulativo.md).
4. **Deploy pela minha plataforma.** O ambiente vivo é publicado pelo agent-platform, que ganha suporte a projetos com Compose para isso. Ver [decisão 0002](./decisoes/0002-deploy-pelo-agent-platform.md).
5. **Tudo documentado como história.** Cada etapa termina com o diário preenchido, as provas guardadas e o texto do portfólio atualizado.
6. **Cabe no NAS.** Todo serviço tem limite de memória e CPU. Serviços pesados (Spark, por exemplo) rodam sob demanda, não ficam ligados.

## O NAS

UGREEN DXP4800 GT (UGOS), Ryzen Embedded R2514 com 4 núcleos e 8 threads (x86_64), 22 GB de RAM e 2 NVMe. A memória é dividida com Forgejo, Dokploy, o control plane do agent-platform e o próprio site portfólio. Dados de containers ficam em `/volume2/docker`. A exposição pública passa pelo Cloudflare Tunnel em `*.pescicloud.com`.

**Meta de orçamento para o ambiente de dados:** até ~8 GB residentes. Os valores abaixo são estimativas iniciais e serão substituídos pelo consumo medido em cada etapa.

## Etapas

O [README](../README.md#como-a-nuvemstore-evolui) conta a história da empresa em cinco fases. O [índice técnico](./indice-tecnico.md) relaciona essas fases aos capítulos. A tabela abaixo acompanha as entregas e publicações no NAS, incluindo a entrega intermediária de dbt e BI.

| Etapa | Capítulos | Entra no ambiente vivo | Memória estimada (acumulada) | Prova principal | Status |
|---|---|---|---|---|---|
| **1. Fundação batch** | 00, 02, 03, 04 | Postgres OLTP, warehouse Postgres, seeder, simulador diário de pedidos, ELT agendado para DuckDB | ~1,5 GB | Teste de ponta a ponta no CI e contagens origem = destino | Em andamento |
| 2. Transformação e BI | 01, 05 | dbt (job), Metabase com rota pública | ~3,5 GB | Dashboard de receita no ar | Planejada |
| 3. Fontes e orquestração | 06, 07 | API mock da transportadora, Airflow (LocalExecutor) no lugar do cron | ~6 GB | DAG com retry e backfill | Planejada |
| 4. Lake e lakehouse | 08, 09, 10 | MinIO interno e Spark sob demanda. HDFS no laboratório de migração | a medir em staging | Equivalência HDFS/MinIO e funil gold em Delta | [Em validação](./diario/etapa-4.md) |
| 5. Baixa latência e ML | 11, 12, 13 | Redpanda, Kafka Connect/Debezium, tabela de features | a medir; pode exigir desligar partes da etapa 4 | Lag do CDC e métricas ao vivo | Planejada |
| 6. Produção e capstone | 14, 15, 16, 17 | Portão de qualidade, SLOs e alertas. Capítulo 14 (LocalStack) fica só no modo local | a medir | Galeria de provas e diagrama consolidado | Planejada |

### Etapa 1 em detalhe

**Objetivo:** a fundação batch roda localmente, no CI e no NAS, com dados novos todo dia.

1. Restaurar o código dos capítulos 00, 02, 03 e 04 a partir dos `SOLUTION.md`, como arquivos reais.
2. Alinhar `.env.example`, RUNBOOKs e composes (hoje divergem em nomes de variáveis e de serviços).
3. Converter os `SOLUTION.md` desses capítulos para o novo papel: explicar as decisões e apontar os arquivos, sem repetir o código (ver [padrão](./padrao-do-repositorio.md#papel-de-cada-documento)).
4. Confirmar a primeira execução do [teste de ponta a ponta no CI](../.github/workflows/ci.yml). O job sobe o Compose do capítulo 04, popula a origem, executa o lote duas vezes e confere contagens e receita por dia.
5. Corrigir os status do README raiz.
6. Criar o ambiente vivo em `deploy/nas/`:
   - `docker-compose.yml` com `oltp`, `warehouse`, `seeder` (job), `simulador` (job), `pipeline` (job) e `agendador` (serviço que executa o lote diário dentro da imagem dos jobs);
   - `docker-compose.staging.yml` com volume de dados menor e limites reduzidos;
   - `.platform/app.json` no formato compose do agent-platform;
   - `.env.example` com as chaves obrigatórias.
7. Publicar no NAS pelo agent-platform (depende da [lista de pré-requisitos da plataforma](./deploy-nas-agent-platform.md#o-que-a-plataforma-precisa-oferecer)).
8. Criar o script e a branch da [trilha sem soluções](./trilha-sem-solucoes.md).
9. Escrever o primeiro texto do projeto no site, com status "em implementação" ([portfolio-site.md](./portfolio-site.md)).
10. Fechar o [diário da etapa 1](./diario/etapa-1.md) e criar a tag `etapa-1`.

O simulador diário é código novo, que não existe nos `SOLUTION.md`: sem ele o ambiente vivo teria sempre os mesmos 1.200 pedidos, e o ELT agendado não teria o que fazer.

### Definição de pronto (vale para toda etapa)

- [ ] Cada capítulo da etapa sobe sozinho seguindo o RUNBOOK, numa máquina limpa.
- [ ] O CI passa, incluindo o teste de ponta a ponta da etapa.
- [ ] O README raiz mostra o status correto.
- [ ] O ambiente vivo no NAS está atualizado, com limites de memória medidos e anotados.
- [ ] A trilha sem soluções foi regenerada.
- [ ] O diário da etapa está completo, com provas (prints, saídas de comando, links).
- [ ] O texto do portfólio foi atualizado.
- [ ] A PR foi revisada e mesclada na `main`, e a tag `etapa-N` foi criada.

## Fluxo de trabalho

1. Uma branch por etapa (`etapa-N`), aberta a partir da `main`.
2. Commits pequenos, em português, no formato `tipo(capítulo): descrição` (ver [padrão](./padrao-do-repositorio.md#commits-e-branches)).
3. PR para a `main` ao fim da etapa. Nada vai para a `main` sem revisão.
4. O commit mesclado vai para a branch `staging` do Forgejo, e o agent-platform publica o staging no NAS.
5. Tag `etapa-N` nesse commit: abre a aprovação de produção no agent-platform (ver [deploy-nas-agent-platform.md](./deploy-nas-agent-platform.md#fluxo-de-uma-etapa-até-o-nas)).

## Riscos conhecidos

| Risco | Como lidar |
|---|---|
| Memória do NAS acabar nas etapas 4 e 5 | Medir a cada etapa; Spark e jobs pesados sob demanda; desligar serviços de etapas anteriores que viraram legado na história (ex.: o warehouse Postgres depois do lakehouse) |
| Suporte a Compose no agent-platform atrasar | O código e o CI de cada etapa não dependem do NAS; o deploy da etapa espera a plataforma |
| `SOLUTION.md` e código divergirem | O código é a fonte da verdade; o `SOLUTION.md` passa a apontar para os arquivos em vez de copiá-los |
| Trilha sem soluções desatualizar | Gerada por script a partir da `main`, nunca editada à mão |

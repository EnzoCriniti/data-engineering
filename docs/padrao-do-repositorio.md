# Padrão do repositório

> Regras para todo capítulo e todo arquivo. Quando um capítulo for implementado, ele é ajustado a este padrão na mesma etapa.

## Estrutura da raiz

```text
data-engineering/
├── README.md                 # a jornada, o status de cada capítulo, como ler o repo
├── COMPANY.md                # o domínio da NuvemStore (fonte de todas as decisões)
├── 00-…/ a 17-…/             # um capítulo por pasta
├── shared/                   # código reaproveitado por vários capítulos (quando houver)
├── system-design/            # arquitetura macro da empresa
├── deploy/nas/               # o ambiente vivo cumulativo publicado no NAS
├── .platform/app.json        # manifesto lido pelo agent-platform
├── tools/                    # scripts do repositório (ex.: gerar a trilha sem soluções)
├── docs/                     # plano, padrões, decisões e diário (esta pasta)
└── .github/workflows/ci.yml  # validação de sintaxe + testes de ponta a ponta
```

## Estrutura de um capítulo

```text
NN-nome-do-capitulo/
├── README.md          # a narrativa: cenário, por que existe, conceitos, a dor que sobra
├── GUIDE.md           # a aula: decisões de design, o que construir, armadilhas, checklist
├── SOLUTION.md        # o gabarito comentado: por que o código é assim, apontando os arquivos
├── RUNBOOK.md         # como subir e usar: comandos, saída esperada, validações
├── TECHNICAL.md       # história da tecnologia, internals, alternativas e tradeoffs
├── .env.example       # toda variável que o compose usa, com valor de desenvolvimento
├── docker-compose.yml # o ambiente do capítulo, quando houver
├── diagrams/          # architecture.py (diagrama como código) + PNG gerado pelo CI
└── <código>/          # seed/, pipeline/, dbt/, airflow/dags/, spark/jobs/ …
```

### Papel de cada documento

| Documento | Responde | Tem comandos? | Tem código completo? |
|---|---|---|---|
| `README.md` | Por que este capítulo existe? | Não | Não |
| `GUIDE.md` | O que construir e quais decisões tomar? | Pouco | Não, só trechos que ensinam |
| `SOLUTION.md` | Por que a solução ficou assim? | Validações | **Não.** Aponta para os arquivos reais, com trechos curtos comentados |
| `RUNBOOK.md` | Como subir e conferir? | Sim | Não |
| `TECHNICAL.md` | Como a tecnologia funciona por dentro? | Não | Não |

A regra do `SOLUTION.md` muda em relação à versão anterior do repositório: o código deixa de ser copiado para dentro do Markdown. **O arquivo real é a fonte da verdade**, e o `SOLUTION.md` explica as escolhas apontando para ele (ex.: "veja `seed/seed.py`, função `gerar_pedidos`"). Isso evita que documento e código divirjam e permite gerar a [trilha sem soluções](./trilha-sem-solucoes.md) só removendo arquivos.

### Seções obrigatórias

- **README:** "De onde viemos" (estado final do capítulo anterior), "O problema", "Arquitetura", "Conceitos", "A dor que sobra".
- **GUIDE:** "Pré-requisitos", "Conceitos fundamentais", uma seção "Etapa N" por arquivo ou grupo de arquivos (Contexto, Decisões de design, O que fazer, Armadilhas), "Checklist final" (operacional e de compreensão).
- **RUNBOOK:** "O que este capítulo entrega", "Pré-requisitos", "Subir", "Usar", "Validar" (com saída esperada), "Recomeçar do zero", "Próximo passo".

## Convenções de código

### Docker Compose

- Imagens com versão fixa (`postgres:16`, nunca `latest`).
- Todo valor configurável vem do `.env` com padrão no compose: `${OLTP_PORT:-5435}`. O `.env.example` lista **todas** as variáveis usadas.
- Senhas de desenvolvimento só no `.env.example`. No ambiente vivo, as senhas vêm dos secrets da plataforma.
- `healthcheck` em todo serviço com estado, e `depends_on: { condition: service_healthy }` em quem depende dele.
- Jobs (seeder, pipeline, migração) ficam no perfil `jobs` e rodam com `docker compose run --rm <job>`.
- Prefixo de container por capítulo: `pNN-<serviço>` (ex.: `p04-oltp`), para dois capítulos não colidirem.
- Portas de host diferentes por capítulo, documentadas no `.env.example`.
- No ambiente vivo (`deploy/nas/`), além disso:
  - todo serviço declara `mem_limit` e `cpus`;
  - só volumes nomeados, sem `name:` fixo nem `external` (nada de bind mount relativo, que some a cada deploy);
  - sem `container_name` (o prefixo `pNN-` é só do modo estudo), sem `ports`, `privileged` ou `docker.sock`;
  - acesso externo só por rota da plataforma.

### Python

- Python 3.12, `requirements.txt` com versões fixas.
- Configuração só por variável de ambiente; sem credencial no código.
- Jobs idempotentes: rodar duas vezes produz o mesmo estado.
- Todo job imprime ao final um resumo verificável (ex.: contagens por tabela) e sai com código diferente de zero em erro.

### SQL

- DDL re-executável (`IF NOT EXISTS`).
- Nomes de negócio em português (`pedido`, `cliente`), prefixos técnicos em inglês (`dim_`, `fct_`, `stg_`, `bronze/silver/gold`).

## Status dos capítulos

| Selo | Significado | Quando pode ser usado |
|---|---|---|
| 📄 Documentado | Só documentação | O código ainda não existe |
| Em validação | Código disponível na etapa em desenvolvimento | Execução reproduzível ou teste de ponta a ponta no CI ainda pendente |
| 🟡 Ambiente base | Os serviços sobem, sem job que mova dado | O compose sobe e o RUNBOOK confere os serviços |
| 🟢 Implementado | Jobs reais movem ou transformam dados | Roda localmente **e** passa no teste de ponta a ponta do CI |
| 🌐 No ar | Faz parte do ambiente vivo no NAS | Publicado pelo agent-platform e com prova no diário |

## Commits e branches

- Uma branch por etapa: `etapa-N`. Correções pequenas fora de etapa: `fix/<assunto>`.
- Mensagens em português, no formato `tipo(escopo): descrição`. Tipos: `feat`, `fix`, `docs`, `test`, `ci`, `chore`, `deploy`. Escopo: número do capítulo, `nas`, `docs` ou `repo`. Exemplo: `feat(04): pipeline ELT incremental para DuckDB`.
- Nada vai para a `main` sem PR revisada. A tag `etapa-N` marca o commit publicado no NAS.
- A branch `trilha-exercicios` é gerada por script; nunca recebe commit à mão.
- A branch antiga `master` é o primeiro rascunho do repositório e já foi mesclada na `main`. Pode ser apagada no GitHub quando eu decidir.

## Diagramas

`diagrams/architecture.py` com a biblioteca `diagrams`; o CI gera e commita o PNG. Diagramas manuais vão para `assets/`.

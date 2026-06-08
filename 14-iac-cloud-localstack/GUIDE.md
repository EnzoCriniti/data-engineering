# Cap. 14 — Infra como código: provisionar o lake com Terraform

> **Aula deste capítulo.** Você aprende a descrever infraestrutura como código declarativo e versionado, validando contra um emulador de nuvem (LocalStack) sem gastar nada. O conceito está aqui; os arquivos `.tf` e o compose estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (provider override, tfstate, comparação com CloudFormation/Pulumi) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

A plataforma toda foi criada à mão até aqui. Isso funciona no laptop, mas não escala: ninguém consegue recriar o ambiente de forma confiável, revisar uma mudança de infra num pull request, ou garantir que staging e produção são idênticos. A infra como código resolve exatamente isso — a infraestrutura passa a ser um artefato versionado, revisável e reproduzível.

O desafio prático do portfólio é provar essa competência sem uma conta de nuvem cobrando. O LocalStack permite escrever Terraform **real** e aplicá-lo contra um emulador local.

## Pré-requisitos

- **Capítulos anteriores:** lakehouse (10) entendido — é o storage que estamos provisionando.
- **Docker:** versão 24+ com Docker Compose.
- **Terraform** instalado localmente (ou via o container do compose).

## Conceitos fundamentais

### Declarativo vs imperativo

Um script imperativo (`aws s3 mb s3://datalake`) diz *como* chegar lá, passo a passo, e quebra se rodado duas vezes (o bucket já existe). Terraform é **declarativo**: você descreve o estado final desejado, e a ferramenta calcula o diff entre o que existe e o que deveria existir. Rodar de novo não faz nada se já está no estado certo.

### O estado (tfstate)

O Terraform mantém um arquivo de estado que mapeia cada bloco do seu HCL ao recurso real correspondente. É esse mapa que permite a ele saber: "o bucket já existe e está como declarado → não faço nada" vs "o versionamento mudou → atualizo". Sem o estado, ele não saberia distinguir criar de atualizar.

### plan antes de apply

`terraform plan` é um *dry-run*: lê o estado atual, compara com o HCL e imprime exatamente o que seria criado/alterado/destruído — sem tocar em nada. É a revisão de segurança. Só depois `terraform apply` executa.

**Exemplo trabalhado — o `plan` que evita o desastre.** Imagine que você edita o HCL para renomear o bucket de `datalake` para `data-lake`. Parece inofensivo. Mas o `terraform plan` revela a verdade: `- aws_s3_bucket.lake` (destroy) seguido de `+ aws_s3_bucket.lake` (create). Renomear um bucket no Terraform não é renomear — é **destruir e recriar**, e com ele vão todos os objetos dentro. O `plan` mostrou isso *antes* de qualquer dano. Esse hábito — ler o plan, procurar por `destroy` onde você não esperava — é o que separa quem usa IaC com segurança de quem aprende na dor.

### LocalStack: AWS emulada localmente

O LocalStack sobe um endpoint (`http://localhost:4566`) que fala as APIs da AWS. O provider AWS do Terraform é configurado para apontar para esse endpoint em vez do real. O HCL não muda; só a configuração do provider (endpoint + credenciais fake). Em produção, você remove o override de endpoint e usa credenciais reais — o resto do código é idêntico.

**Exemplo trabalhado — o mesmo código, dois destinos.** O bloco `resource "aws_s3_bucket" "lake"` que você escreve é literalmente o mesmo que rodaria contra a AWS de verdade. A única diferença vive no bloco `provider`: localmente ele tem `endpoints { s3 = "http://localhost:4566" }` e credenciais `test/test`; em produção, esse bloco some e o Terraform usa as credenciais reais do ambiente. É isso que torna o LocalStack honesto para portfólio — você não está aprendendo um brinquedo, está escrevendo a infra real e só trocando para onde ela aponta.

### Idempotência da infra

O mesmo princípio dos pipelines: aplicar duas vezes leva ao mesmo estado. `terraform apply` rodado de novo, sem mudanças no HCL, reporta "No changes". Isso é o que permite usar IaC em automação (CI) com segurança.

---

## Etapa 1 — Subir o LocalStack (`docker-compose.yml`)

### O que fazer
Um serviço único: a imagem `localstack/localstack`, expondo a porta `4566` (o gateway único de todas as APIs emuladas) e declarando `SERVICES=s3` para subir só o que precisamos.

### Decisões de design
- *Só S3 habilitado*: LocalStack emula dezenas de serviços; habilitar só `s3` deixa a subida rápida e o escopo claro.
- *Porta 4566 única*: diferente da AWS real (vários endpoints), o LocalStack centraliza tudo num gateway. O Terraform aponta o endpoint de cada serviço para essa porta.

---

## Etapa 2 — Escrever o provider e o backend (`terraform/provider.tf`)

### Contexto
O bloco `provider "aws"` é onde mora toda a diferença entre local e produção. Aqui ele recebe credenciais fake, região qualquer, e o override de endpoint apontando para o LocalStack.

### Decisões de design
- *Credenciais fake (`test`/`test`)*: o LocalStack não valida credenciais; usar valores óbvios deixa claro que não há segredo real.
- *`s3_use_path_style = true`*: o LocalStack serve buckets por path (`localhost:4566/datalake`) e não por subdomínio. Mesma razão do `path.style.access` que o MinIO exigiu no cap 10.
- *`skip_credentials_validation` e afins*: desligam as chamadas de verificação que só fazem sentido contra a AWS real.

### ⚠️ Armadilhas
- Esquecer o `s3_use_path_style`: o Terraform tenta `datalake.localhost` e falha na resolução.
- Deixar o override de endpoint hardcoded num arquivo que vai para produção: parametrize via variável para que produção simplesmente não o defina.

---

## Etapa 3 — Declarar o recurso do lake (`terraform/main.tf`)

### O que fazer
Declarar o bucket `datalake`, um recurso de versionamento habilitado, e (opcional) uma política de acesso. Tudo em HCL declarativo.

### Decisões de design
- *Versionamento ligado*: um lake de produção quer histórico de objetos — alinha com a filosofia append-only/time-travel dos caps 10–11.
- *Nome via variável*: o nome do bucket vem de uma `variable`, com default `datalake`, para não repetir string mágica.

### ⚠️ Armadilhas
- Renomear o bucket no HCL pensando que é um rename: é destroy+create (veja o exemplo trabalhado). Sempre leia o `plan`.
- Aplicar sem `plan` antes: você perde a chance de ver mudanças destrutivas.

### 📚 Para se aprofundar
- [Terraform AWS Provider — S3 bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)
- [LocalStack — Terraform integration](https://docs.localstack.cloud/user-guide/integrations/terraform/)

---

## Etapa 4 — Aplicar e validar

### O que fazer
`terraform init` (baixa o provider), `terraform plan` (revisa), `terraform apply` (cria). Depois, validar com a AWS CLI apontada para o LocalStack: listar buckets e conferir que o versionamento está habilitado.

### ⚠️ Armadilhas
- Validar com a CLI sem o `--endpoint-url http://localhost:4566`: ela tenta a AWS real e não acha nada.

---

## ✅ Checklist final

Operacional:

- [ ] LocalStack sobe e responde em `http://localhost:4566`
- [ ] `terraform init` baixa o provider sem erro
- [ ] `terraform plan` mostra a criação do bucket antes do apply
- [ ] `terraform apply` cria o bucket `datalake`
- [ ] AWS CLI (com `--endpoint-url`) lista o bucket e confirma versionamento
- [ ] `terraform apply` rodado de novo reporta "No changes" (idempotência)

Compreensão (você entendeu — responda sem olhar):

- [ ] Qual a diferença entre `terraform plan` e `terraform apply`, e por que separar os dois importa?
- [ ] Conte o caso do `plan` que evita o desastre: por que renomear um bucket é destrutivo?
- [ ] O que muda no código entre rodar contra o LocalStack e contra a AWS real? (Quase nada — o quê exatamente?)
- [ ] Para que serve o tfstate? O que o Terraform não conseguiria fazer sem ele?

## A dor que sobra

A infra é reproduzível, mas a plataforma ainda assume que o dado que entra é válido. Um payload de API que mudou ou um nulo inesperado passa despercebido até estourar num dashboard. O próximo capítulo trata disso: **qualidade e contratos de dados**.

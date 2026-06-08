# Capítulo 14 — Infra como código: deploy de nuvem com Terraform (LocalStack) 🟡

> **De onde viemos:** os capítulos 00–13 entregam uma plataforma completa — OLTP, warehouse, ELT, dbt, Airflow, lake/lakehouse, CDC, streaming e base de ML. Tudo roda em Docker, no laptop, e tudo é **criado à mão**: cada `docker compose up`, cada bucket no MinIO, cada banco. A dor que sobra é a primeira pergunta de qualquer entrevista de produção: *"como isso sobe na nuvem, de forma reproduzível, sem alguém clicar em console?"*

## Cenário de negócio

A NuvemStore decidiu mover o lake para a nuvem. O problema não é só *onde* o storage vive — é **como** ele é provisionado. Criar bucket na mão, configurar política de acesso clicando no console e versionar nada disso é como a equipe perdeu uma tarde inteira quando precisou recriar o ambiente de staging: ninguém lembrava a configuração exata.

A resposta é **infra como código (IaC)**: a infraestrutura vira um arquivo versionado no Git. Quem lê o repositório entende exatamente quais recursos existem, e `terraform apply` recria tudo de forma idêntica — em staging, em produção, ou na máquina de um colega novo.

## O dilema do portfólio: provisionar nuvem sem queimar dinheiro

Apontar Terraform para uma conta AWS pessoal é o caminho clássico para uma fatura surpresa: um recurso esquecido ligado, egress alto, um cluster que ninguém derrubou. Para um portfólio de estudo, o risco não compensa.

A solução é o **LocalStack**: um emulador da AWS que roda como container Docker e responde às mesmas APIs (S3, IAM, etc.) num endpoint local. O Terraform é **real** — o mesmo HCL que rodaria contra a AWS de verdade — só que aponta para `http://localhost:4566` em vez do endpoint da Amazon. Custo zero, nenhum cartão exposto, e a competência demonstrada é exatamente a mesma: modelar infra declarativa e versionada.

```text
Terraform (HCL real)  ->  provider AWS  ->  endpoint LocalStack (local)  ->  bucket S3 "emulado"
                                              (em produção, trocaria só o endpoint)
```

## O que esta etapa mostra

O provisionamento do storage do lake como código: um módulo Terraform que cria o bucket `datalake`, habilita versionamento e configura uma política de acesso — declarado em `.tf`, aplicado contra o LocalStack, e validável com a AWS CLI apontada para o mesmo endpoint.

## Conceitos

**Infra como código (IaC).** A infraestrutura é descrita em arquivos versionados, não em cliques. O estado desejado mora no Git; a ferramenta reconcilia o mundo real com o que está declarado.

**Declarativo vs imperativo.** Terraform é declarativo: você descreve o *estado final* ("quero um bucket com versionamento"), não os passos. A ferramenta calcula o que criar, alterar ou destruir.

**Plan vs apply.** `terraform plan` mostra o que *seria* feito sem tocar em nada — é a revisão de segurança da infra. `terraform apply` materializa. Separar os dois é o que evita mudança acidental em produção.

**Estado (tfstate).** O Terraform guarda um mapa entre o HCL e os recursos reais. É por isso que ele sabe a diferença entre criar e atualizar. Em time, esse estado vive remoto e travado; aqui, local.

**Idempotência.** Aplicar duas vezes não cria dois buckets. O mesmo princípio de idempotência dos pipelines (cap 04, 06, 07) vale para a infra.

**LocalStack como ambiente de teste.** Permite validar o Terraform sem custo nem conta. O mesmo código sobe na AWS real trocando apenas o endpoint e as credenciais.

> Detalhamento técnico (provider override, tfstate, Terraform vs CloudFormation vs Pulumi) em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base / documentação.** O compose sobe o LocalStack; o módulo Terraform provisiona o bucket do lake contra ele. O passo-a-passo está no [GUIDE.md](./GUIDE.md) e o código no [SOLUTION.md](./SOLUTION.md).

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o LocalStack, aplicar o Terraform e validar o bucket (com espaço para prints da execução).

## A dor que sobra

A infra agora é reproduzível, mas o pipeline ainda confia que os dados que chegam estão corretos. Quando a API externa do cap 06 muda o payload silenciosamente, ou o OLTP manda um valor nulo onde não deveria, nada quebra de forma visível — o dado ruim só aparece num dashboard errado, dias depois. O próximo capítulo ataca isso: **qualidade e contratos de dados**.

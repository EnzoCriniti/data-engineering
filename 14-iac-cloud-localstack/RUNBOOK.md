# Runbook — Capítulo 14: infra como código com Terraform + LocalStack

> Guia rápido para **subir e usar**. Status atual: **ambiente base** — o LocalStack sobe pronto; o módulo Terraform que provisiona o bucket do lake é o roteiro do [GUIDE.md](./GUIDE.md) (código no [SOLUTION.md](./SOLUTION.md)).

## O que este capítulo entrega hoje

Um emulador de AWS (LocalStack) rodando localmente e um módulo Terraform que provisiona o storage do lake (`datalake`) com versionamento — tudo como código versionado, custo zero, sem conta de nuvem.

## Pré-requisitos

- Docker e Docker Compose.
- Terraform 1.5+ instalado localmente.
- AWS CLI (para validação).
- Porta `4566` livre (confira no `.env.example`).

## Subir o ambiente

```bash
cp .env.example .env
docker compose up -d
```

## Provisionar a infra

```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

## Validar

```bash
aws --endpoint-url http://localhost:4566 s3 ls
aws --endpoint-url http://localhost:4566 s3api get-bucket-versioning --bucket datalake
```

Esperado: o bucket `datalake` aparece na listagem e o versionamento está `Enabled`. Rodar `terraform apply` de novo reporta "No changes" (idempotência).

## Prints da execução

> Coloque aqui as capturas de tela conforme for resolvendo o capítulo. Salve os arquivos em [`assets/`](./assets/). Eles ajudam quem lê o repositório a ver o resultado sem subir o ambiente.

Sugestões do que capturar:

- `terraform plan` mostrando a criação do bucket — `assets/14-terraform-plan.png`
- `terraform apply` concluído com "Apply complete!" — `assets/14-terraform-apply.png`
- `aws s3 ls` listando o bucket via endpoint do LocalStack — `assets/14-bucket-listado.png`

<!--
![terraform plan](./assets/14-terraform-plan.png)
![terraform apply](./assets/14-terraform-apply.png)
![bucket listado](./assets/14-bucket-listado.png)
-->

## Recomeçar do zero

```bash
cd terraform && terraform destroy -auto-approve && cd ..
docker compose down -v
```

## Próximo passo

[Capítulo 15](../15-qualidade-contratos-dados): garantir que o dado que entra na plataforma é válido, com testes de qualidade e contratos de schema.

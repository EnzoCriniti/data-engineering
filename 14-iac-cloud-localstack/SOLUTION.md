# Solução — Cap. 14: Infra como código com Terraform + LocalStack

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
14-iac-cloud-localstack/
├── docker-compose.yml
└── terraform/
    ├── provider.tf
    ├── variables.tf
    ├── main.tf
    └── outputs.tf
```

## `docker-compose.yml`

Sobe apenas o LocalStack com o serviço S3 habilitado. A porta `4566` é o gateway único de todas as APIs emuladas.

```yaml
services:
  localstack:
    image: localstack/localstack:3
    container_name: p14-localstack
    ports:
      - "${LOCALSTACK_PORT:-4566}:4566"
    environment:
      SERVICES: s3
      DEBUG: ${LOCALSTACK_DEBUG:-0}
    volumes:
      - localstack-data:/var/lib/localstack

volumes:
  localstack-data:
```

## `terraform/provider.tf`

Todo o "truque" local vive aqui: credenciais fake, validações desligadas e o endpoint do S3 apontando para o LocalStack. Em produção, o bloco `endpoints` e as credenciais fake somem; o resto não muda.

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"

  # Em produção: remover o bloco abaixo e usar credenciais reais.
  s3_use_path_style           = true   # LocalStack/MinIO servem bucket por path
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = var.localstack_endpoint
  }
}
```

## `terraform/variables.tf`

```hcl
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "localstack_endpoint" {
  type    = string
  default = "http://localhost:4566"
}

variable "bucket_name" {
  type    = string
  default = "datalake"
}
```

## `terraform/main.tf`

Declara o bucket do lake e habilita versionamento. HCL puramente declarativo — descreve o estado final, não os passos.

```hcl
resource "aws_s3_bucket" "lake" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "lake" {
  bucket = aws_s3_bucket.lake.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

## `terraform/outputs.tf`

```hcl
output "bucket_name" {
  value = aws_s3_bucket.lake.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.lake.arn
}
```

## Como testar

```bash
# 1) Sobe o LocalStack
docker compose up -d

# 2) Provisiona a infra (dentro de terraform/)
cd terraform
terraform init
terraform plan      # revisa: deve mostrar a criação do bucket + versionamento
terraform apply -auto-approve

# 3) Valida com a AWS CLI apontando para o LocalStack
aws --endpoint-url http://localhost:4566 s3 ls
aws --endpoint-url http://localhost:4566 s3api get-bucket-versioning --bucket datalake

# 4) Prova de idempotência: rodar de novo não muda nada
terraform apply -auto-approve   # deve reportar "No changes"
```

Esperado: `s3 ls` lista o bucket `datalake`; `get-bucket-versioning` retorna `"Status": "Enabled"`; o segundo `apply` reporta "No changes. Your infrastructure matches the configuration."

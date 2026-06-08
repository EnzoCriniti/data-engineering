# Complemento técnico — Terraform, estado e emulação de nuvem

## O que este capítulo aprofunda

Este capítulo mostra que infraestrutura também é software: versionada, revisável e reproduzível. O diferencial não é "saber clicar no console da AWS" — é descrever a infra de forma declarativa, entender o ciclo plan/apply e o papel do estado, e validar tudo sem custo via emulação.

## Pequena história

Antes do IaC, infra era provisionada manualmente ou com scripts shell imperativos — frágeis e não reproduzíveis. A AWS lançou o **CloudFormation** em 2011, trazendo templates declarativos, mas amarrados à AWS. Em 2014, a HashiCorp lançou o **Terraform**, com duas ideias que o popularizaram: ser *cloud-agnostic* (um mesmo workflow para AWS, GCP, Azure e centenas de providers) e usar uma linguagem própria (HCL) focada em legibilidade. Mais tarde surgiu o **Pulumi** (2018), que troca o HCL por linguagens de programação reais (Python, TypeScript).

O **LocalStack** (2017) nasceu de outra dor: testar código que fala com a AWS sem pagar nem depender de rede. Ele emula as APIs dos serviços AWS num container, e virou ferramenta padrão para testes de integração e aprendizado.

## Por baixo dos panos

### O ciclo plan/apply e o estado

O Terraform funciona em três tempos: lê o **estado** (o que ele acha que existe), consulta o **mundo real** (refresh) e compara com o **HCL** (o desejado). O `plan` é o diff dessas três coisas; o `apply` executa o diff.

O arquivo de estado (`terraform.tfstate`) é o que torna isso possível. Ele mapeia cada bloco `resource` a um ID real. Sem ele, o Terraform não saberia que o bucket que ele criou ontem é o mesmo que está no HCL hoje — trataria tudo como novo.

Em time, esse estado **não** fica no laptop: vive num backend remoto (S3 + DynamoDB para lock, ou Terraform Cloud) para que ninguém aplique em cima do outro. Aqui, por ser didático e local, o estado é um arquivo na pasta.

### Por que LocalStack não exige mudar o código

O provider AWS do Terraform aceita um override de `endpoints`. Apontá-lo para `http://localhost:4566` faz todas as chamadas irem para o LocalStack em vez da AWS. Os blocos `resource` — a parte que descreve a infra — são idênticos aos de produção. Essa separação entre *o que* (resources) e *para onde* (provider) é o que permite o mesmo código rodar nos dois ambientes.

### Idempotência e o operador de reconciliação

Terraform é essencialmente um reconciliador: ele converge o mundo real para o estado declarado. Aplicar N vezes leva ao mesmo lugar. Isso é o que permite usá-lo em CI: um pipeline pode rodar `terraform apply` a cada merge sem medo de duplicar recursos.

## Por que entra depois da base de ML

Até o cap 13, o foco era *o que* a plataforma faz. A partir daqui, o foco é *como ela vira produção*: provisionamento reproduzível (14), qualidade de dados (15) e observabilidade (16). IaC vem primeiro porque é o alicerce — sem infra reproduzível, os controles seguintes rodam sobre areia.

## Tecnologias equivalentes

| Ferramenta | Quando usar |
| --- | --- |
| Terraform | Padrão de mercado, cloud-agnostic, ecossistema enorme de providers. |
| CloudFormation / CDK | Quem é 100% AWS e quer integração nativa; CDK usa linguagens reais. |
| Pulumi | Quem prefere Python/TypeScript a uma DSL própria. |
| Ansible | Mais voltado a configuração de máquinas do que a provisionamento de nuvem. |
| LocalStack | Testar/aprender infra AWS sem custo nem conta. |

## Quando usar

Use IaC sempre que a infra precisar ser reproduzível, revisável ou recriável — ou seja, quase sempre em produção. Para um experimento descartável de cinco minutos, o console é mais rápido; para tudo que vai durar, código.

Use LocalStack para desenvolvimento, testes de integração e portfólio. Para validar comportamento específico de um serviço gerenciado (latência real, limites, IAM detalhado), só a nuvem real resolve.

## Como isso aparece no projeto

Este capítulo transforma o storage do lake — antes um bucket criado à mão no MinIO — em infraestrutura declarada. É a ponte entre "roda no meu Docker" e "sobe na nuvem de forma reproduzível", sem expor o autor a custos.

## 📚 Referências

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs) — documentação oficial.
- [LocalStack Docs](https://docs.localstack.cloud/) — serviços emulados e integrações.
- [Terraform: Up & Running (Yevgeniy Brikman)](https://www.terraformupandrunning.com/) — referência prática de IaC.
- [LocalStack + Terraform](https://docs.localstack.cloud/user-guide/integrations/terraform/) — guia de integração oficial.

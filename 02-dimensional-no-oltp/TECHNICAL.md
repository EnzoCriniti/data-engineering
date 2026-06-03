# Complemento técnico - Analytics no mesmo banco transacional

## O que esta etapa aprofunda

Esta etapa mostra uma decisão histórica comum: criar o modelo dimensional dentro do próprio banco transacional, geralmente em outro schema. E barato, rapido e facil de comecar, mas cria disputa de recursos.

## Por que empresas fizeram isso

No comeco, o volume e pequeno e a equipe quer responder perguntas rapidamente. Criar um schema `analytics` no mesmo banco parece natural:

- não precisa provisionar outro banco;
- não precisa pipeline complexo;
- as tabelas de origem já estao perto;
- o time consegue entregar relatorios cedo.

Esse padrão aparece muito em empresas pequenas, sistemas internos e fases iniciais de produto.

## Por baixo dos panos

Mesmo com schemas diferentes, o banco compartilha os mesmos recursos:

- CPU;
- memória;
- disco;
- conexões;
- WAL;
- autovacuum;
- índices;
- locks e catálogos.

Consultas analíticas tendem a fazer scans e agregações. Transações OLTP precisam responder rapido. Quando as duas convivem no mesmo servidor, uma carga analítica pode aumentar latência do sistema de negócio.

## Separacao lógica vs separacao física

Separacao lógica organiza objetos. Separacao física isola recursos.

Um schema `analytics` e separacao lógica. Dois bancos em containers diferentes, com volumes e conexões separados, já demonstram separacao física.

## Tecnologias equivalentes

| Abordagem | Caracteristica |
| --- | --- |
| Mesmo banco, outro schema | Barato, simples, mas divide recursos. |
| Read replica para analytics | Reduz impacto na escrita, mas ainda depende da origem. |
| Warehouse dedicado | Isola carga analítica e permite modelagem própria. |
| Data mart por área | Separa consumo por domínio, mas exige governanca. |

## Quando usar

Use quando o volume e baixo, o SLA e flexível e o objetivo e provar valor rapidamente.

Evite quando consultas analíticas já afetam o produto, quando ha muitos usuários de BI ou quando a origem precisa de alta disponibilidade.

## Como isso conecta a trilha

Esta etapa cria a dor operacional que justifica a etapa seguinte: separar o warehouse da origem. Sem sentir essa disputa, a separacao parece excesso de arquitetura.

# Complemento tecnico - Analytics no mesmo banco transacional

## O que esta etapa aprofunda

Esta etapa mostra uma decisao historica comum: criar o modelo dimensional dentro do proprio banco transacional, geralmente em outro schema. E barato, rapido e facil de comecar, mas cria disputa de recursos.

## Por que empresas fizeram isso

No comeco, o volume e pequeno e a equipe quer responder perguntas rapidamente. Criar um schema `analytics` no mesmo banco parece natural:

- nao precisa provisionar outro banco;
- nao precisa pipeline complexo;
- as tabelas de origem ja estao perto;
- o time consegue entregar relatorios cedo.

Esse padrao aparece muito em empresas pequenas, sistemas internos e fases iniciais de produto.

## Por baixo dos panos

Mesmo com schemas diferentes, o banco compartilha os mesmos recursos:

- CPU;
- memoria;
- disco;
- conexoes;
- WAL;
- autovacuum;
- indices;
- locks e catalogos.

Consultas analiticas tendem a fazer scans e agregacoes. Transacoes OLTP precisam responder rapido. Quando as duas convivem no mesmo servidor, uma carga analitica pode aumentar latencia do sistema de negocio.

## Separacao logica vs separacao fisica

Separacao logica organiza objetos. Separacao fisica isola recursos.

Um schema `analytics` e separacao logica. Dois bancos em containers diferentes, com volumes e conexoes separados, ja demonstram separacao fisica.

## Tecnologias equivalentes

| Abordagem | Caracteristica |
| --- | --- |
| Mesmo banco, outro schema | Barato, simples, mas divide recursos. |
| Read replica para analytics | Reduz impacto na escrita, mas ainda depende da origem. |
| Warehouse dedicado | Isola carga analitica e permite modelagem propria. |
| Data mart por area | Separa consumo por dominio, mas exige governanca. |

## Quando usar

Use quando o volume e baixo, o SLA e flexivel e o objetivo e provar valor rapidamente.

Evite quando consultas analiticas ja afetam o produto, quando ha muitos usuarios de BI ou quando a origem precisa de alta disponibilidade.

## Como isso conecta a trilha

Esta etapa cria a dor operacional que justifica a etapa seguinte: separar o warehouse da origem. Sem sentir essa disputa, a separacao parece excesso de arquitetura.

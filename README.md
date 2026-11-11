# NuvemStore — portfólio de engenharia de dados

A NuvemStore é um e-commerce brasileiro fictício com frota própria. A loja começou com um site, um backend e um único PostgreSQL. O checkout gravava pedidos, itens e preços. Pagamentos e despachos mudavam de status na mesma base. Quando o Comercial passou a pedir a receita diária por categoria, os relatórios começaram a dividir recursos com o checkout. [Contexto da empresa](./COMPANY.md#como-a-loja-funcionava-no-início)

## Comece pela demonstração

A primeira entrega já foi executada com **1.200 pedidos sintéticos**. O ELT copiou oito tabelas do PostgreSQL para o DuckDB. A contagem e a receita dos 1.033 pedidos não cancelados bateram entre origem e destino em duas execuções.

- [Reproduzir a demonstração](./04-elt-batch-com-python/RUNBOOK.md)
- [Conferir os resultados](./docs/diario/etapa-1.md#provas)
- [Ver os guias de todos os capítulos](./docs/indice-tecnico.md)

## Como a NuvemStore evolui

### 1. Do checkout à receita diária

**Em validação.** A equipe desenha o modelo de vendas e cria um schema analítico no mesmo Postgres. Como checkout e relatórios ainda compartilham recursos, a análise passa para um warehouse dedicado. O lote em Python e DuckDB demonstra a carga e a reconciliação de receita. [Guias da fundação batch](./docs/indice-tecnico.md#1-do-checkout-à-receita-diária)

### 2. Entregas com múltiplas fontes

**Planejada.** A loja terceiriza parte das entregas. Logística precisa cruzar as ocorrências da transportadora com os pedidos para acompanhar atrasos. A entrega prevista é um indicador de SLA calculado com dbt a partir de uma carga que pode ser reexecutada. [Guias de transformação e ingestão](./docs/indice-tecnico.md#2-entregas-com-múltiplas-fontes)

### 3. Histórico de navegação

**Planejada.** Produto quer entender onde os clientes abandonam a compra. Os eventos de navegação exigem guardar e consultar um histórico maior em JSON. A entrega prevista é um funil consultável no lakehouse. O guia de migração acompanha a passagem de HDFS para object storage e a conferência do histórico. [Guias de lake e lakehouse](./docs/indice-tecnico.md#3-histórico-de-navegação)

### 4. Decisões durante o dia

**Planejada.** Operações precisa ver a frota em segundos, enquanto Risco quer acompanhar mudanças de pagamento. A demonstração vai seguir um evento de GPS até a métrica e uma atualização de pagamento até o destino do CDC. A base de fraude estende esse cenário. [Guias de baixa latência](./docs/indice-tecnico.md#4-decisões-durante-o-dia)

### 5. Operação confiável

**Planejada.** Com várias áreas dependendo dos dados, a equipe precisa recuperar cargas, detectar mudanças nas fontes e saber quando uma tabela ficou defasada. A demonstração vai reunir uma recuperação de carga, um dado rejeitado por contrato e um alerta de atraso. [Guias de operação e capstone](./docs/indice-tecnico.md#5-operação-confiável)

## Acompanhe o projeto

- [Plano de implementação e publicações no NAS](./docs/plano-de-implementacao.md)
- [Arquitetura e decisões da plataforma](./system-design)
- [Verificações automatizadas](./.github/workflows/ci.yml)

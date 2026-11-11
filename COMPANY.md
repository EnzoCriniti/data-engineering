# NuvemStore — contexto de negócio e fontes de dados

> **Documento de referência do domínio.** Toda decisão de modelagem e arquitetura neste repositório parte daqui. A plataforma de dados é projetada para *esta* empresa, com *estas* fontes e *estas* necessidades — exatamente como no mundo real, onde o domínio vem antes da ferramenta.

## Visão de negócio

A **NuvemStore** começa como um e-commerce brasileiro com frota própria nas regiões onde atua. Na primeira fase, a prioridade é registrar pedidos e atender ao checkout. Com o crescimento, a empresa terceiriza parte das entregas, amplia a coleta de dados de navegação e passa a acompanhar operações e pagamentos com mais frequência. A empresa tem três frentes de dados:

1. **Loja online** — catálogo de produtos, carrinho, checkout e pagamentos.
2. **Navegação dos clientes** — todo o comportamento no site (páginas vistas, buscas, cliques) que alimenta marketing e produto.
3. **Entregas próprias** — frota de entregadores rastreada por GPS em tempo real.

Os volumes da tabela de fontes representam o cenário de crescimento da empresa fictícia. A demonstração da fundação batch usa uma amostra sintética de 1.200 pedidos.

## Como a loja funcionava no início

O cliente navegava pelo catálogo, montava o carrinho e fechava a compra pelo site. O backend registrava o pedido e seus itens no PostgreSQL, guardava o preço de cada item no momento da compra e acompanhava o status do pagamento. A operação de entregas usava o mesmo banco para associar o pedido a um entregador da frota própria e registrar o despacho.

O banco era transacional, ou OLTP. Cadastro de clientes, catálogo, pedidos, pagamentos e entregas eram domínios da mesma aplicação e compartilhavam a mesma instância. O modelo mantinha cada informação no lugar em que era atualizada. Uma alteração no catálogo, por exemplo, preservava o preço registrado nos pedidos anteriores.

Quando o Comercial passou a pedir receita diária e vendas por categoria, os relatórios começaram a consultar a base da loja. Para calcular a receita de uma categoria, era preciso combinar pedidos, itens, produtos e categorias, aplicar o filtro de cancelamentos e agregar o histórico. Enquanto isso, o checkout continuava criando pedidos e a operação atualizava pagamentos e entregas no mesmo banco.

A primeira tentativa foi criar um schema analítico no PostgreSQL para organizar os dados por venda, produto e tempo. O banco continuou compartilhando CPU, memória e I/O entre relatórios e checkout. A próxima mudança foi dedicar outra instância às análises e carregar os dados em lote. [Arquitetura da empresa](./system-design/company-architecture.md) · [Primeiro ambiente analítico](./02-dimensional-no-oltp)

## Estrutura organizacional (quem consome dado)

| Área | O que precisa | Latência tolerada |
|------|---------------|-------------------|
| **Comercial / BI** | Receita, ticket médio, top produtos, vendas por região | Diária |
| **Marketing / Produto** | Funil de conversão, comportamento de navegação, retenção | Diária / horária |
| **Risco / Pagamentos** | Detecção de fraude em transações | Quase tempo real |
| **Operações / Logística** | Entregas ativas, tempo médio, anomalias da frota | Tempo real (segundos) |
| **Finanças** | Fechamento, histórico, auditoria | Sob demanda (histórico) |

Essa diversidade de latências é o que justifica, sozinha, uma arquitetura que vai de batch a streaming.

## Sistemas e fontes de dados

| # | Fonte | Sistema | Natureza | Formato | Volume aprox. |
|---|-------|---------|----------|---------|---------------|
| F1 | **Banco transacional** | App da loja | OLTP (Postgres) | Tabelas relacionais | ~20k pedidos/dia |
| F2 | **Eventos de navegação** | Front-end do site | Semi-estruturado | JSON (cliques, page views) | ~500k eventos/dia |
| F3 | **Eventos de GPS** | App dos entregadores | Streaming | Eventos contínuos (posição, velocidade, status) | ~50 eventos/s |
| F4 | **Ocorrências de entrega** | Transportadora parceira | Batch | API HTTP/JSON | Diário |

## Entidades principais (domínio)

O núcleo transacional gira em torno de:

- **Cliente** — quem compra (nome, contato, localização).
- **Produto** — o que é vendido, organizado em **categorias**.
- **Pedido** — uma compra, composta de vários **itens de pedido**.
- **Pagamento** — a transação financeira de um pedido (a fonte do CDC de fraude).
- **Entrega** — o despacho de um pedido, associado a um **entregador** e rastreado por **eventos de GPS**.

Esses são os candidatos naturais a **dimensões** (cliente, produto, entregador, tempo, região) e **fatos** (vendas, entregas) no modelo analítico.

## Necessidades futuras por capítulo (por que modelamos assim)

Esta é a tabela que **guia as decisões de modelagem dos capítulos 00 e 01**: modelamos hoje pensando em tudo que a plataforma vai exigir adiante.

| Necessidade de negócio | Fonte | Capítulo que resolve | Exigência que isso impõe à modelagem |
|------------------------|-------|----------------------|--------------------------------------|
| Relatório de receita e produtos mais vendidos | F1 | [02](./02-dimensional-no-oltp) a [05](./05-transformacao-com-dbt) | Fato de vendas, dimensões de produto e tempo, e regras de cálculo verificáveis |
| Histórico de mudanças de cliente | F1 | [01](./01-modelagem-dimensional) (desenho dimensional) | Dimensão cliente com **SCD Tipo 2** |
| SLA das entregas terceirizadas | F4 e F1 | [06](./06-ingestao-api-externa) a [07](./07-orquestracao-com-airflow) | Chave de pedido para reconciliar ocorrências externas e vendas |
| Funil de conversão e navegação | F2 | [08](./08-data-lake-com-spark) a [10](./10-lakehouse-medallion) | Histórico de eventos semiestruturados para análises de Marketing e Produto |
| Custo e retenção do histórico | Todas | [09](./09-migracao-hdfs-para-s3) | Particionamento por data e reconciliação entre os armazenamentos |
| Métricas de entrega ao vivo | F3 | [12](./12-streaming-kappa) | Eventos de GPS com horário do evento e chave de entregador |
| Detecção de fraude | F1 (pagamentos) e histórico da plataforma | [11](./11-cdc-com-debezium) e [13](./13-base-ml-fraude) | Chave estável no CDC e atributos disponíveis no instante da decisão |

> **A lição:** as surrogate keys, o SCD2 na dimensão cliente, o particionamento por data e a separação de pagamentos como entidade própria **não são decisões arbitrárias** — cada uma existe para atender uma necessidade já mapeada acima. Modelar sem esse contexto seria adivinhar.

## Convenções

- Empresa, nomes e dados são **fictícios**; os geradores de cada capítulo produzem dados sintéticos (Faker) coerentes com este domínio.
- Português nos nomes de negócio; inglês onde for convenção técnica (ex: `fct_`, `dim_`, `bronze/silver/gold`).

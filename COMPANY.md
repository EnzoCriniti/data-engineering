# NuvemStore — contexto de negócio e fontes de dados

> **Documento de referência do domínio.** Toda decisão de modelagem e arquitetura neste repositório parte daqui. A plataforma de dados é projetada para *esta* empresa, com *estas* fontes e *estas* necessidades — exatamente como no mundo real, onde o domínio vem antes da ferramenta.

## Visão de negócio

A **NuvemStore** é um e-commerce brasileiro de médio porte com **logística própria**: além de vender online, opera a própria frota de entregadores nas regiões onde atua. O negócio se sustenta em três pilares operacionais:

1. **Loja online** — catálogo de produtos, carrinho, checkout e pagamentos.
2. **Navegação dos clientes** — todo o comportamento no site (páginas vistas, buscas, cliques) que alimenta marketing e produto.
3. **Entregas próprias** — frota de entregadores rastreada por GPS em tempo real.

A empresa cresceu rápido e hoje sofre as dores clássicas de quem escalou sem plataforma de dados: relatórios lentos, decisões com dado defasado e nenhuma visão unificada. Esta plataforma resolve isso, capítulo a capítulo.

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
| F4 | **Catálogo / parceiros** | Integrações | Batch | CSV/API (logística, marketing) | Diário |

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
| Relatório de receita/top produtos | F1 | 02–03 (pipeline + dbt) | Modelo dimensional com fato de vendas e dimensões de produto/tempo |
| Histórico de mudanças de cliente | F1 | 01 (dimensional) | Dimensão cliente com **SCD Tipo 2** |
| Funil de conversão / navegação | F2 | 05–06 (lake + lakehouse) | Eventos semi-estruturados, schema-on-read, camada bronze |
| Detecção de fraude | F1 (pagamentos) | 07 (CDC) | Tabela de pagamentos com chave estável e timestamps para CDC |
| Métricas de entrega ao vivo | F3 | 08 (streaming) | Eventos de GPS com event time e chave de entregador |
| Custo de storage do histórico | todas | 09 (híbrido) | Particionamento por data para tiering quente/frio |

> **A lição:** as surrogate keys, o SCD2 na dimensão cliente, o particionamento por data e a separação de pagamentos como entidade própria **não são decisões arbitrárias** — cada uma existe para atender uma necessidade já mapeada acima. Modelar sem esse contexto seria adivinhar.

## Convenções

- Empresa, nomes e dados são **fictícios**; os geradores de cada capítulo produzem dados sintéticos (Faker) coerentes com este domínio.
- Português nos nomes de negócio; inglês onde for convenção técnica (ex: `fct_`, `dim_`, `bronze/silver/gold`).

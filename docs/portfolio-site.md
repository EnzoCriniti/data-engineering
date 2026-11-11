# Como o projeto entra no site portfólio

## Onde fica

O site é gerado a partir do repositório privado `carreira-portfolio`, arquivo `site/dados/projetos.js`. O repositório `site-portfolio` só recebe a cópia publicada (`node tools/publicar_site.mjs`) e **nunca é editado direto**. Antes de publicar, `npm run checar` valida os dados e as regras de escrita.

## O bloco do projeto

Cada projeto do site segue o formato Problema → Decisão → Solução → Como funciona → Resultados, em português e inglês. Para este projeto:

| Campo | Valor |
|---|---|
| `id` | `plataforma-dados-nuvemstore` |
| `categoria` | `data` |
| `status` | `wip` até a etapa 3; `prod` quando o ambiente vivo tiver ingestão, transformação, BI e orquestração no ar |
| `destaque` | `true` a partir da etapa 2 (quando houver dashboard público para mostrar) |
| `origem` | `pessoal` |
| `repositorio` | `https://github.com/EnzoCriniti/data-engineering` |
| `tecnologias` | só o que já está implementado na etapa publicada |

## Rascunho para a etapa 1

> Rascunho para revisar com calma antes de ir para o site. Segue as regras de escrita do portfólio: sem percentuais, sem valores em dinheiro, cada frase começando de um jeito diferente, tecnologias só do que existe.

- **Título:** NuvemStore — do banco de pedidos aos marts de vendas
- **Resumo:** Projeto de engenharia de dados que acompanha a evolução de um e-commerce fictício. A primeira etapa leva os pedidos do PostgreSQL a tabelas analíticas no DuckDB.
- **Problema:** No início, um único PostgreSQL atende o checkout, os pagamentos e as entregas da frota própria. Quando o Comercial começa a acompanhar a receita diária e os produtos mais vendidos, os relatórios cruzam o histórico de pedidos e itens na mesma instância em que a loja continua vendendo.
- **Decisão:** Modelei as vendas em um schema analítico no próprio Postgres para mostrar o que a separação por schema resolve. Como checkout e relatórios ainda compartilham recursos, separei o banco analítico e construí uma carga em lote. Mantive a mesma regra de receita para poder conferir o resultado em cada ambiente.
- **Solução (etapa 1):** Implementei um gerador de dados sintéticos para o PostgreSQL e um ELT batch em Python. O pipeline carrega as tabelas da origem no DuckDB e materializa os marts de receita diária e produtos mais vendidos.
- **Como funciona:**
  1. O seeder popula o PostgreSQL com clientes, produtos e pedidos sintéticos.
  2. O pipeline copia as tabelas para o DuckDB e calcula os indicadores de vendas.
  3. A demonstração compara a contagem de pedidos e a receita entre a origem e o mart.
  4. O [runbook](../04-elt-batch-com-python/RUNBOOK.md) mostra como reproduzir a execução.
- **Resultados:** Em uma amostra de 1.200 pedidos sintéticos, conferi a contagem de oito tabelas entre PostgreSQL e DuckDB. A receita dos 1.033 pedidos não cancelados bateu com a origem em duas execuções do mesmo lote. [Evidência da execução](./diario/etapa-1.md#provas)
- **Papel:** Modelei a origem, desenvolvi o pipeline batch e documentei como reproduzir e conferir o resultado.
- **Tecnologias (etapa 1):** Python, PostgreSQL, DuckDB, SQL e Docker Compose.

O teste de ponta a ponta no CI, o agendamento e a publicação no NAS entram no case conforme forem validados. As evidências ficam no [diário da etapa 1](./diario/etapa-1.md).

## Como contar a evolução no site

A página começa pela primeira entrega, **Do checkout à receita diária**. A evolução prevista aparece em quatro blocos curtos, **Entregas com múltiplas fontes**, **Histórico de navegação**, **Decisões durante o dia** e **Operação confiável**. Cada bloco recebe uma evidência à medida que é validado. Os [guias técnicos](./indice-tecnico.md) ficam no repositório.

O case abre com o que Comercial consegue demonstrar hoje. O leitor pode seguir para o [passo a passo](../04-elt-batch-com-python/RUNBOOK.md) ou abrir a [história da empresa](../COMPANY.md). Para apresentar o restante da trilha, conecte cada decisão ao time que passa a depender dos dados:

> A NuvemStore começa com um site, um backend e um PostgreSQL. A mesma base guarda o que o cliente comprou, o preço no momento da venda, o status do pagamento e quem fará a entrega. O primeiro relatório do Comercial usa essas tabelas para responder quanto a loja vendeu por categoria. A equipe organiza as consultas em um schema analítico e, quando a disputa por recursos chega ao checkout, leva as análises para um banco dedicado.
>
> Quando a NuvemStore terceiriza parte das entregas, Logística precisa juntar ocorrências da transportadora com os pedidos. Marketing e Produto passam a acompanhar a navegação antes da compra, o que amplia o volume e o histórico de dados. Já Operações e Risco precisam de respostas durante o dia para acompanhar a frota e as mudanças nos pagamentos. À medida que mais times passam a usar a plataforma, recriar o ambiente, validar os dados e detectar atrasos viram requisitos.

Ao publicar uma etapa, associe a mudança a uma evidência concreta, como uma reconciliação de receita, uma recuperação de carga ou um alerta de atraso.

A versão em inglês é escrita depois que o texto em português estiver aprovado.

## Proposta de página

O card da NuvemStore entra na listagem de projetos em Engenharia de Dados, com status `wip` e o link **Acompanhar a evolução**. O link abre uma página própria dentro de Projetos, na rota `#/projetos/plataforma-dados-nuvemstore`.

1. **Abertura.** “O que acontece quando os relatórios começam a disputar recursos com o checkout?” Uma introdução curta explica a loja e leva ao resultado.
2. **Primeira decisão.** Um diagrama em três quadros acompanha as consultas no OLTP, o schema analítico na mesma instância e o warehouse dedicado. Em seguida, o fluxo PostgreSQL → Python → DuckDB mostra a demonstração do ELT.
3. **Evidência.** Mostrar 1.200 pedidos sintéticos, oito tabelas conferidas e duas execuções com receita conciliada. Incluir links para o diário, o repositório e o runbook.
4. **Evolução.** As outras quatro fases aparecem em uma linha do tempo. Cada fase planejada tem uma pergunta de negócio e o resultado que se espera demonstrar.

Manter a tipografia, o azul de Dados e os temas do site. Usar uma coluna de leitura com índice lateral no desktop e uma sequência vertical no celular. Os atalhos de seção preservam a rota para permitir copiar o link e usar voltar e avançar.

No repositório `carreira-portfolio`, começar pelos dados em português e inglês em `site/dados/projetos.js` e pelo roteamento em `site/app.js`. Adicionar a área da página em `site/index.html` e o layout em `site/styles.css`. Manter os cases em modal para os demais projetos. Validar com `npm run checar` e conferir acesso direto, teclado, temas e celular no preview antes de publicar.

## Atualização a cada etapa

Ao fechar uma etapa:

1. atualizar "Solução", "Como funciona", "Resultados" e "Tecnologias" com o que entrou;
2. trocar números estimados por medidos (vêm do diário da etapa);
3. revisar o texto em inglês;
4. rodar `npm run checar` e publicar o site.

## Relação com o projeto agent-platform no site

O agent-platform já está no site como projeto pessoal. Quando o suporte a Compose estiver pronto, o case dele ganha uma frase sobre publicar projetos de dados com vários serviços, apontando para este projeto. Os dois cases se citam: um mostra a plataforma de dados, o outro a plataforma que a publica.

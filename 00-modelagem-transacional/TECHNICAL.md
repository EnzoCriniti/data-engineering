# Complemento técnico - Modelagem transacional e PostgreSQL

## O que este capítulo aprofunda

Este capítulo usa um modelo OLTP normalizado como origem da NuvemStore. O foco técnico é entender por que bancos relacionais continuam sendo a base de sistemas transacionais: consistência, integridade referencial, transações pequenas e escrita concorrente.

## Pequena história

O modelo relacional foi proposto por Edgar F. Codd em 1970, como uma forma matemática de representar dados em relações, ou tabelas. Antes disso, sistemas hierárquicos e em rede exigiam navegação mais manual entre registros.

O PostgreSQL vem do projeto POSTGRES, iniciado na Universidade da Califórnia em Berkeley na década de 1980. A versão chamada PostgreSQL surgiu na década de 1990, quando o projeto passou a usar SQL como linguagem principal. Hoje ele é uma das principais escolhas open source para bancos relacionais robustos.

## Por baixo dos panos

Um banco OLTP é otimizado para muitas operações pequenas: criar pedido, atualizar pagamento, inserir item de pedido. Para isso, ele usa transações ACID.

- Atomicidade: uma transação acontece inteira ou não acontece.
- Consistência: constraints, PKs e FKs impedem estados inválidos.
- Isolamento: transações simultâneas não devem se corromper.
- Durabilidade: depois do commit, o dado precisa sobreviver a falhas.

O PostgreSQL usa MVCC, ou Multi-Version Concurrency Control. Em vez de bloquear toda leitura quando alguém escreve, ele mantém versões das linhas. Isso permite que leitores vejam uma fotografia consistente do banco enquanto escritores continuam trabalhando.

Outro componente importante é o WAL, Write-Ahead Log. Antes de aplicar alterações de forma definitiva, o banco registra a mudança em log. Esse mecanismo dá durabilidade e também viabiliza replicação e CDC, explorado no capítulo 11.

## Normalização

Normalizar significa separar entidades para reduzir redundância e anomalias de atualizacao. Neste projeto, categoria fica separada de produto; cliente fica separado de pedido; item_pedido resolve a relação entre pedido e produto.

Isso melhora escrita e consistência, mas piora leitura analítica. Uma pergunta simples como "receita por categoria" exige várias joins. Essa dor é exatamente o motivo do capítulo 01.

## Tecnologias equivalentes

| Tecnologia | Onde se encaixa |
| --- | --- |
| MySQL / MariaDB | Relacionais populares para aplicações web e OLTP. |
| SQL Server | Forte em ambientes corporativos Microsoft. |
| Oracle Database | Muito usado em grandes empresas, com alto custo e muitos recursos enterprise. |
| SQLite | Banco embarcado, excelente para apps locais e testes. |
| MongoDB | Documento, não relacional; bom para schemas flexíveis, mas com outro modelo de consistência e consulta. |

## Quando usar

Use um banco relacional transacional quando o sistema precisa de integridade forte: pedidos, pagamentos, estoque, contratos, cadastros e qualquer domínio em que dados inválidos custam caro.

Evite usar o OLTP como motor analítico pesado. Queries grandes competem com o checkout, o cadastro e as atualizacoes de negócio. Em plataformas de dados, a origem transacional deve ser extraída para uma camada analítica.

## Como isso aparece no projeto

O arquivo `ddl/schema.sql` define a origem canônica da NuvemStore. O seeder popula essa origem com dados sintéticos e os capítulos seguintes tratam esse Postgres como sistema de produção a ser protegido.

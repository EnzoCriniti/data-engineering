# Complemento tecnico - Modelagem transacional e PostgreSQL

## O que este capitulo aprofunda

Este capitulo usa um modelo OLTP normalizado como origem da NuvemStore. O foco tecnico e entender por que bancos relacionais continuam sendo a base de sistemas transacionais: consistencia, integridade referencial, transacoes pequenas e escrita concorrente.

## Pequena historia

O modelo relacional foi proposto por Edgar F. Codd em 1970, como uma forma matematica de representar dados em relacoes, ou tabelas. Antes disso, sistemas hierarquicos e em rede exigiam navegacao mais manual entre registros.

O PostgreSQL vem do projeto POSTGRES, iniciado na Universidade da California em Berkeley na decada de 1980. A versao chamada PostgreSQL surgiu na decada de 1990, quando o projeto passou a usar SQL como linguagem principal. Hoje ele e uma das principais escolhas open source para bancos relacionais robustos.

## Por baixo dos panos

Um banco OLTP e otimizado para muitas operacoes pequenas: criar pedido, atualizar pagamento, inserir item de pedido. Para isso, ele usa transacoes ACID.

- Atomicidade: uma transacao acontece inteira ou nao acontece.
- Consistencia: constraints, PKs e FKs impedem estados invalidos.
- Isolamento: transacoes simultaneas nao devem se corromper.
- Durabilidade: depois do commit, o dado precisa sobreviver a falhas.

O PostgreSQL usa MVCC, ou Multi-Version Concurrency Control. Em vez de bloquear toda leitura quando alguem escreve, ele mantem versoes das linhas. Isso permite que leitores vejam uma fotografia consistente do banco enquanto escritores continuam trabalhando.

Outro componente importante e o WAL, Write-Ahead Log. Antes de aplicar alteracoes de forma definitiva, o banco registra a mudanca em log. Esse mecanismo da durabilidade e tambem viabiliza replicacao e CDC, explorado no capitulo 10.

## Normalizacao

Normalizar significa separar entidades para reduzir redundancia e anomalias de atualizacao. Neste projeto, categoria fica separada de produto; cliente fica separado de pedido; item_pedido resolve a relacao entre pedido e produto.

Isso melhora escrita e consistencia, mas piora leitura analitica. Uma pergunta simples como "receita por categoria" exige varias joins. Essa dor e exatamente o motivo do capitulo 01.

## Tecnologias equivalentes

| Tecnologia | Onde se encaixa |
| --- | --- |
| MySQL / MariaDB | Relacionais populares para aplicacoes web e OLTP. |
| SQL Server | Forte em ambientes corporativos Microsoft. |
| Oracle Database | Muito usado em grandes empresas, com alto custo e muitos recursos enterprise. |
| SQLite | Banco embarcado, excelente para apps locais e testes. |
| MongoDB | Documento, nao relacional; bom para schemas flexiveis, mas com outro modelo de consistencia e consulta. |

## Quando usar

Use um banco relacional transacional quando o sistema precisa de integridade forte: pedidos, pagamentos, estoque, contratos, cadastros e qualquer dominio em que dados invalidos custam caro.

Evite usar o OLTP como motor analitico pesado. Queries grandes competem com o checkout, o cadastro e as atualizacoes de negocio. Em plataformas de dados, a origem transacional deve ser extraida para uma camada analitica.

## Como isso aparece no projeto

O arquivo `ddl/schema.sql` define a origem canonica da NuvemStore. O seeder popula essa origem com dados sinteticos e os capitulos seguintes tratam esse Postgres como sistema de producao a ser protegido.

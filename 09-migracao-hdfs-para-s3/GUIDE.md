# Guia — Migrar e provar equivalência

## Pré-requisitos

Docker Compose v2 em Linux. O laboratório recria a origem HDFS a partir do gerador do capítulo 08.

## Conceitos fundamentais

O teste precisa verificar o conteúdo lido do destino e a semântica de uma consulta de negócio. Contagens, schema e limites de data ajudam a localizar diferenças. Compare os multiconjuntos para preservar duplicatas.

## Etapa 1 — Escrever o candidato

Leia o snapshot congelado de eventos e pedidos. Calcule o hash do conteúdo em ordem canônica. Grave o destino em um prefixo próprio e releia o Parquet do MinIO.

## Etapa 2 — Verificar e promover

Compare schema e `EXCEPT ALL` nos dois sentidos. Normalize e execute o mesmo funil por sessão e por coorte na origem e no destino. Grave o manifesto depois da equivalência e faça o consumidor ler apenas prefixos registrados.

## Checklist final

- [ ] A evidência identifica origem, destino, hash e partições.
- [ ] Alterar um payload sem mudar o total falha na comparação.
- [ ] Com HDFS parado, o resultado permanece consultável no MinIO.

[Operação](./RUNBOOK.md) · [Detalhes de armazenamento](./TECHNICAL.md)

# Guia — Ingerir histórico de navegação

## Pré-requisitos

Docker Compose v2 em Linux para o laboratório. Python 3.11 ou superior para gerar e inspecionar o NDJSON.

## Conceitos fundamentais

O timestamp do evento é UTC. A data física da partição deriva desse horário. A coorte de negócio usa o calendário de São Paulo e pode ler duas partições UTC.

## Etapa 1 — Modelar a fonte

Defina o contrato v1 com ID de evento, sessão, sequência e tipo. Use sequência crescente para desempatar horários iguais. A confirmação de compra exige ID de pedido. Gere casos determinísticos de duplicata, evento inválido, compra fora da janela e compra que cruza a meia-noite UTC.

## Etapa 2 — Congelar o snapshot

Use NameNode e DataNode no perfil `hdfs`. Em Spark local, grave Parquet com o texto original, particione por dia UTC e mantenha a partição `invalido`. Promova o diretório candidato por rename após gravar eventos e pedidos.

## Checklist final

- [ ] Repetir a geração produz os mesmos bytes.
- [ ] As duas datas UTC e a partição de inválidos aparecem no HDFS.
- [ ] Reexecutar a ingestão confirma o mesmo hash e o mesmo número de linhas.

[Operação](./RUNBOOK.md) · [Detalhes de HDFS e Parquet](./TECHNICAL.md)

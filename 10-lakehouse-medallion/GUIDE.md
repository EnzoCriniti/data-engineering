# Guia — Da navegação ao funil em Delta

## Pré-requisitos

Docker Compose v2 em Linux para executar Spark e MinIO. Python 3.11 ou superior para a verificação rápida do SQL.

## Conceitos fundamentais

Bronze preserva os envelopes imutáveis. Silver modela identidade e valida os eventos. Gold materializa uma métrica por coorte, com versão reexecutável.

## Etapa 1 — Silver

Valide o contrato e retenha o bruto para auditoria. Remova retries idênticos. Falhe se um ID ou sequência representar dois eventos distintos. Reconheça uma compra quando o pedido aparece como pago no snapshot e o cliente informado coincide, quando presente.

## Etapa 2 — Funil Gold

A primeira visualização determina a coorte em São Paulo. Busque, por sessão, o primeiro evento de cada etapa posterior ao passo precedente e a menos de 30 minutos da visualização. Conte sessões, calcule a diferença e a perda relativa por etapa e guarde os IDs dos pedidos convertidos.

## Etapa 3 — Reprocessamento

Persista versões Delta. Registre o manifesto de entrada e a versão silver usada pela gold. Reexecute o mesmo conjunto de lotes para testar estabilidade. Acrescente um lote tardio e leia a versão anterior para recuperar o resultado original.

## Checklist final

- [ ] O lote base dá `4 → 3 → 2 → 1`, com uma conversão ligada a pedido pago.
- [ ] Uma linha inválida e um retry ficam fora da contagem silver.
- [ ] O lote tardio dá `4 → 3 → 2 → 2` e a versão anterior continua legível.

[Operação](./RUNBOOK.md) · [Detalhes de Delta](./TECHNICAL.md)

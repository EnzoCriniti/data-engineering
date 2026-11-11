# Solução — Cap. 03: Warehouse dedicado

O [Compose](./docker-compose.yml) separa o OLTP e o warehouse em duas instâncias PostgreSQL com seus próprios volumes. O [DDL do destino](./warehouse/schema.sql) materializa o modelo dimensional nesse segundo banco. O [arquivo de exemplo](./.env.example) descreve as portas e a [imagem do job](./warehouse/Dockerfile) instala os [requisitos](./warehouse/requirements.txt) da migração.

A [migração](./warehouse/migrate.py) reconstrói as dimensões em uma transação no destino e usa `dblink` para ler os itens elegíveis da origem. A fato resolve as chaves substitutas por data, cliente atual e produto. A carga exclui pedidos cancelados e usa o preço registrado no item. Como a reconstrução substitui as tabelas de destino, execute a migração com a origem estável para reconciliar os mesmos dados.

## Validações

Siga o [runbook](./RUNBOOK.md) para executar a migração e conferir a fato. O job compara a contagem de itens e a receita da origem e do warehouse e retorna erro se houver divergência. O [diário](../docs/diario/etapa-1.md#provas) registra a conciliação de 3.188 itens.

# Solução — Cap. 00: Modelagem transacional

O [modelo DBML](./modeling/nuvemstore_oltp.dbml) mostra as relações do checkout. O [DDL](./ddl/schema.sql) separa cabeçalho, itens, pagamentos e entregas. O preço unitário fica no item para preservar o valor da compra quando o catálogo muda. Uma chave única em `(pedido_id, produto_id)` impede repetir um produto no mesmo pedido. Cada pedido admite várias tentativas de pagamento e até uma entrega.

O [seeder](./seed/seed.py) usa sementes fixas de Faker e random para gerar o cenário didático, com datas relativas ao dia de execução. Os [requisitos](./seed/requirements.txt) e o [Dockerfile](./seed/Dockerfile) fixam o ambiente. Com o reset padrão, a truncagem, o reinício das identidades e as inserções ficam na mesma transação. Use esse modo em um banco descartável. A opção de comportamentos suspeitos usada no capítulo 13 gera eventos sem atribuir rótulo de fraude.

## Validações

Siga o [runbook](./RUNBOOK.md) para conferir as oito tabelas, 250 clientes e 1.200 pedidos. Repita o seed com reset e confira que as contagens permanecem iguais e que a consulta de integridade retorna zero itens órfãos.

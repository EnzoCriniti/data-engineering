# Solução — Cap. 02: Dimensional no OLTP

O [Compose](./docker-compose.yml) inicializa o modelo transacional e depois aplica o [DDL analítico](./ddl/analytics.sql) na mesma instância. O schema `analytics` dá um namespace próprio a três dimensões e à fato, mas as consultas ainda dividem CPU, memória e I/O com o checkout.

A fato tem grão de item de pedido e aponta para as dimensões de tempo, cliente e produto por chaves substitutas. A dimensão de cliente inclui vigência e indicador de registro atual para representar SCD tipo 2. A carga das dimensões e da fato entra no capítulo seguinte.

## Validações

Use o [runbook](./RUNBOOK.md) e a [configuração de exemplo](./.env.example). Confira as oito tabelas transacionais com os pedidos sintéticos e quatro tabelas vazias em `analytics`.

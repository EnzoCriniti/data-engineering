# Solução — Cap. 04: ELT batch com Python e DuckDB

O [Compose](./docker-compose.yml) sobe o OLTP e expõe o seeder e o ELT como jobs. A [configuração de exemplo](./.env.example) indica a porta local. A [imagem do pipeline](./pipeline/Dockerfile) instala os [requisitos](./pipeline/requirements.txt) de Python e grava o banco DuckDB no diretório de dados.

O [pipeline](./pipeline/pipeline.py) reconstrói oito tabelas `raw_*` com colunas de texto. A transformação faz os casts e usa o preço registrado no item para calcular a receita diária e o ranking dos 20 produtos por receita. Os marts incluem pedidos pendentes e pagos e excluem cancelamentos. O full refresh permite reprocessar a origem sem acumular duplicatas.

## Validações

O [verificador](./pipeline/verify.py) compara as contagens raw e a quantidade de pedidos e a receita por dia com consultas independentes ao PostgreSQL. Também confere o tamanho do ranking e retorna erro em caso de divergência. O [runbook](./RUNBOOK.md) reproduz as duas execuções definidas no [CI](../.github/workflows/ci.yml). O [diário](../docs/diario/etapa-1.md#provas) registra as contagens e a receita conciliadas.

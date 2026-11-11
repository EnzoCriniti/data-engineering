# Runbook — Funil Delta no MinIO

## O que este capítulo entrega

Funil diário por sessão em `s3a://nuvemstore-lake/navegacao/gold/funil_diario`. A silver contém o vínculo com o pedido pago. O relatório inclui contagens, perdas absolutas, taxas e IDs dos pedidos convertidos.

## Pré-requisitos

Docker Compose v2 em Linux para a integração. Python 3.11 ou superior para o teste rápido em SQLite. Rode da raiz.

## Subir

```bash
compose=(docker compose -p nuvemstore-navegacao -f 10-lakehouse-medallion/docker-compose.yml)
mkdir -p 10-lakehouse-medallion/data/evidencias
chmod a+w 10-lakehouse-medallion/data/evidencias
"${compose[@]}" up --build -d --wait minio
"${compose[@]}" build lakehouse
```

## Usar

```bash
# Se o snapshot já foi migrado, rode build. Em um ambiente vazio, rode demo.
"${compose[@]}" run --rm -T lakehouse demo
"${compose[@]}" run --rm -T lakehouse build
"${compose[@]}" run --rm -T lakehouse demo --lote tardio
"${compose[@]}" run --rm -T lakehouse history
```

O demo independente usa dois pedidos de referência sintéticos. O script de integração cria um PostgreSQL isolado com o seeder da fase 2 e verifica a ligação contra o banco.

## Validar

```bash
python3 shared/navegacao/test_fixture.py
bash shared/navegacao/e2e.sh
```

O fluxo completo deve reproduzir `4 → 3 → 2 → 1` e `4 → 3 → 2 → 2` após o lote tardio, rejeitar um candidato adulterado, ler a gold após recriar o MinIO e recuperar a versão anterior. O diretório `10-lakehouse-medallion/data/evidencias/` reúne os JSON e os IDs do PostgreSQL. O script usa projeto Compose descartável e remove seus volumes ao terminar.

## Recomeçar do zero

`"${compose[@]}" down -v` apaga os volumes descartáveis do demo. Para remover também os volumes HDFS do mesmo projeto de estudo, rode com `--profile hdfs`.

## Próximo passo

Confira o [aceite de staging no Agent Platform](../docs/diario/etapa-4.md).

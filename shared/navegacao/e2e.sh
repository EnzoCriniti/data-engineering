#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

export LAKE_REVISION
LAKE_REVISION="$(git rev-parse HEAD)"
project="${LAKE_TEST_PROJECT:-nuvemstore-navegacao-ci}"
lake=(docker compose -p "$project" -f 10-lakehouse-medallion/docker-compose.yml --profile hdfs)
orders=(docker compose -p "$project-oltp" -f 04-elt-batch-com-python/docker-compose.yml)
artifact_dir="10-lakehouse-medallion/data/evidencias"

cleanup() {
  if [[ "$?" -ne 0 ]]; then
    "${lake[@]}" logs --no-color namenode datanode minio || true
  fi
  "${lake[@]}" down -v || true
  "${orders[@]}" down -v || true
}
trap cleanup EXIT

mkdir -p "$artifact_dir"
# O runner Spark usa UID próprio. O diretório contém somente as evidências da demonstração.
chmod a+w "$artifact_dir"
python3 shared/navegacao/test_fixture.py
"${orders[@]}" up -d --wait oltp
"${orders[@]}" run --rm -T -e SEED_CLIENTES=15 -e SEED_PEDIDOS=40 seeder
"${orders[@]}" exec -T oltp psql -U nuvemstore -Atc \
  "SELECT pedido_id FROM pedido WHERE status = 'pago' ORDER BY pedido_id LIMIT 2" > "$artifact_dir/pedidos-fase2.txt"

"${lake[@]}" up --build -d --wait namenode datanode minio
docker network connect --alias oltp-fase2 "${project}_default" p04-oltp
"${lake[@]}" build lakehouse
"${lake[@]}" run --rm -T -e OLTP_HOST=oltp-fase2 -e OLTP_PASSWORD=nuvemstore lakehouse ingest
"${lake[@]}" run --rm -T lakehouse migrate
"${lake[@]}" run --rm -T lakehouse test

"${lake[@]}" stop namenode datanode
"${lake[@]}" rm -sf minio
"${lake[@]}" up -d --wait minio
"${lake[@]}" run --rm -T lakehouse build
cmp "$artifact_dir/gold-base.json" "$artifact_dir/gold.json"
"${lake[@]}" run --rm -T lakehouse demo --lote tardio
"${lake[@]}" run --rm -T lakehouse history

# O Agent Platform começa com bucket vazio e consulta o OLTP sem HDFS.
mv "$artifact_dir/gold.json" "$artifact_dir/gold-tardio.json"
"${lake[@]}" run --rm -T -e LAKE_BUCKET=nuvemstore-staging-smoke \
  -e OLTP_HOST=oltp-fase2 -e OLTP_PASSWORD=nuvemstore lakehouse demo
mv "$artifact_dir/gold.json" "$artifact_dir/gold-sem-hdfs.json"

python3 - "$artifact_dir" <<'PY'
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
base = json.loads((root / "gold-base.json").read_text(encoding="utf-8"))
current = json.loads((root / "gold-tardio.json").read_text(encoding="utf-8"))
direct = json.loads((root / "gold-sem-hdfs.json").read_text(encoding="utf-8"))
history = json.loads((root / "historico.json").read_text(encoding="utf-8"))
ids = [int(i) for i in (root / "pedidos-fase2.txt").read_text().splitlines()]
assert base["resultado"]["pedidos_convertidos"] == ids[:1], base
assert current["resultado"]["pedidos_convertidos"] == ids, current
assert [current["resultado"][step] for step in ("visualizaram", "adicionaram", "iniciaram", "compraram")] == [4, 3, 2, 2]
assert current["versao_gold"] == base["versao_gold"] + 1
assert direct["resultado"] == base["resultado"]
assert direct["versao_gold"] == 0
assert history["versao_anterior"] == base["versao_gold"]
assert history["resultado_anterior"] == base["resultado"]
print(f"HDFS → MinIO → Delta: 4 → 3 → 2 → 1, depois 4 → 3 → 2 → 2. Pedidos OLTP: {ids}")
PY

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

export OLTP_PASSWORD=ci-oltp WAREHOUSE_PASSWORD=ci-warehouse
export TRANSPORTADORA_API_KEY=ci-transportadora AIRFLOW_DB_PASSWORD=ci-metadata
export AIRFLOW_SECRET_KEY=ci-airflow
project="nuvemstore-airflow-test-${GITHUB_RUN_ID:-$$}"
overlay=$(mktemp)
cat > "$overlay" <<'YAML'
services:
  airflow-scheduler:
    environment:
      AIRFLOW__SCHEDULER__USE_JOB_SCHEDULE: "false"
      AIRFLOW_JOB_RETRY_SECONDS: "30"
      API_ATTEMPTS: "1"
YAML
compose() {
  docker compose -p "$project" -f deploy/nas/docker-compose.yml \
    -f deploy/nas/docker-compose.staging.yml -f "$overlay" "$@"
}
airflow() { compose exec -T airflow-scheduler airflow "$@"; }
cleanup() {
  result=$?
  if [ "$result" -ne 0 ]; then
    compose logs --no-color airflow-init airflow-scheduler transportadora || true
    compose exec -T airflow-scheduler sh -c \
      'find /opt/airflow/logs -name "*.log" -exec tail -n 30 {} \;' || true
  fi
  compose down --volumes
  rm -f "$overlay"
  return "$result"
}
trap cleanup EXIT

wait_for() {
  for ((attempt=0; attempt<48; attempt++)); do
    if "$@"; then return 0; fi
    sleep 5
  done
  echo "Tempo excedido aguardando $*" >&2
  return 1
}

compose up -d --build --wait oltp warehouse
compose run --rm --build -T seeder
# Pedido pago terceirizado sem linha em entrega própria. Usa IDs reais.
compose run --rm -T -e SIM_AS_OF=2026-06-08T08:00:00Z simulador
count=$(compose exec -T oltp psql -U nuvemstore -Atc \
  'select count(*) from simulacao_transportadora s left join entrega e using (pedido_id) where e.pedido_id is null')
test "$count" = 3
compose up -d --build --wait --wait-timeout 240 airflow-scheduler

dag_ready() { airflow dags list 2>/dev/null | grep -q nuvemstore_daily; }
wait_for dag_ready
airflow dags unpause nuvemstore_daily
compose stop transportadora
airflow dags trigger nuvemstore_daily --run-id recuperacao --conf '{"somente_reprocessar":true}'
task_is() {
  local actual
  actual=$(airflow tasks state nuvemstore_daily "$1" recuperacao 2>/dev/null | tail -1)
  test "$actual" = "$2"
}
wait_for task_is carga_api up_for_retry
compose up -d --wait transportadora
wait_for task_is verificar_sla success
echo "Airflow: carga_api entrou em up_for_retry e o DAG concluiu após recuperar a API."

state() {
  compose exec -T airflow-scheduler /opt/nuvemstore/.venv/bin/python - <<'PY'
import duckdb
import os

with duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True) as db:
    assert db.execute("select count(*) from staging.transportadora_entregas").fetchone()[0] == 3
    assert db.execute("""
        select count(*) from analytics_dbt.mart_sla_entregas
        where situacao_sla in ('no_prazo', 'atraso_aberto', 'entregue_com_atraso')
    """).fetchone()[0] == 3
    print(db.execute("select * from staging.transportadora_checkpoint").fetchall())
    print(db.execute("select entrega_id, updated_at from staging.transportadora_entregas order by 1").fetchall())
    print(db.execute("select entrega_id, situacao_sla from analytics_dbt.mart_sla_entregas order by 1").fetchall())
PY
}
initial=$(state)
airflow dags backfill nuvemstore_daily --start-date 2026-06-08T06:00:00Z --end-date 2026-06-08T06:00:00Z --yes
test "$(state)" = "$initial"
compose run --rm -T extractor extract --start 2026-06-08T06:00:00Z --end 2026-06-09T06:00:00Z
compose run --rm -T dbt build
test "$(state)" = "$initial"
echo "Airflow: backfill e reexecução manual preservaram chaves, status e checkpoint."

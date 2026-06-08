# Solução — Cap. 16: Observabilidade do pipeline

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
16-observabilidade-pipeline/
├── docker-compose.yml
└── observability/
    ├── requirements.txt
    ├── Dockerfile
    ├── slos.json
    └── collect_metrics.py
```

> O coletor observa o **gold do lakehouse** (cap 10/12) via **Trino** — o mesmo estado consolidado que o cap 15 valida. O gabarito mantém o coletor enxuto (Python + client Trino) para o conceito ficar claro. Em produção, as métricas seriam exportadas para Prometheus e visualizadas no Grafana (ver [TECHNICAL.md](./TECHNICAL.md)).

## `docker-compose.yml`

Coletor em perfil `jobs`, conectando ao Trino do lakehouse pela rede do compose do cap 10 (a forma de ligar os dois ambientes está no RUNBOOK).

```yaml
services:
  observability:
    build: ./observability
    container_name: p16-observability
    volumes:
      - ./observability:/app
    environment:
      TRINO_HOST: ${TRINO_HOST:-trino}
      TRINO_PORT: ${TRINO_PORT:-8080}
      TRINO_CATALOG: ${TRINO_CATALOG:-delta}
      TRINO_SCHEMA: ${TRINO_SCHEMA:-gold}
    profiles: [jobs]
```

## `observability/requirements.txt`

```
trino==0.330.0
```

## `observability/Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "collect_metrics.py"]
```

## `observability/slos.json`

SLOs declarativos por tabela gold: coluna de timestamp para freshness (quando há), limite de atraso (horas) e piso de volume (fração da baseline). A gold de streaming (`velocidade_regional`) tem o `window` como sinal natural de freshness; a gold batch (`resumo_entregas`), agregada por status, não tem timestamp de linha — para ela monitoramos só volume (`ts_column` nulo desliga o check de freshness).

```json
{
  "slos": [
    {
      "table": "velocidade_regional",
      "ts_column": "window",
      "max_freshness_hours": 1,
      "volume_min_ratio": 0.5,
      "volume_baseline": 100
    },
    {
      "table": "resumo_entregas",
      "ts_column": null,
      "max_freshness_hours": 24,
      "volume_min_ratio": 0.5,
      "volume_baseline": 4
    }
  ]
}
```

## `observability/collect_metrics.py`

Calcula freshness e volume por tabela, compara com o SLO, imprime um relatório e sai com código não-zero se algum SLO for violado — pronto para virar uma task final da DAG do Airflow.

```python
"""Coletor de observabilidade: freshness e volume do gold vs SLOs declarados (via Trino)."""
import os, sys, json, logging
from datetime import datetime, timezone
import trino

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CONN = dict(
    host=os.getenv("TRINO_HOST", "trino"),
    port=int(os.getenv("TRINO_PORT", "8080")),
    user="observability",
    catalog=os.getenv("TRINO_CATALOG", "delta"),
    schema=os.getenv("TRINO_SCHEMA", "gold"),
)
SLO_PATH = os.path.join(os.path.dirname(__file__), "slos.json")

def scalar(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]

def freshness_hours(cur, table, ts_col):
    row = scalar(cur, f'SELECT max({ts_col}) FROM {table}')
    if row is None:
        return None
    if isinstance(row, str):
        row = datetime.fromisoformat(row)
    if row.tzinfo is None:
        row = row.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - row).total_seconds() / 3600

def main():
    slos = json.load(open(SLO_PATH))["slos"]
    conn = trino.dbapi.connect(**CONN)
    cur = conn.cursor()
    violacoes = 0

    for slo in slos:
        t = slo["table"]
        log.info(f"--- {t} ---")

        # Freshness (só se a tabela tiver coluna de timestamp)
        if slo.get("ts_column"):
            fh = freshness_hours(cur, t, slo["ts_column"])
            if fh is None:
                log.error("  ❌ freshness: tabela vazia")
                violacoes += 1
            elif fh > slo["max_freshness_hours"]:
                log.error(f"  ❌ freshness: {fh:.1f}h (SLO {slo['max_freshness_hours']}h) — DADO DEFASADO")
                violacoes += 1
            else:
                log.info(f"  ✅ freshness: {fh:.1f}h (SLO {slo['max_freshness_hours']}h)")
        else:
            log.info("  — freshness: sem coluna de timestamp (só volume)")

        # Volume
        n = scalar(cur, f'SELECT count(*) FROM {t}')
        piso = slo["volume_baseline"] * slo["volume_min_ratio"]
        if n < piso:
            log.error(f"  ❌ volume: {n} linhas (piso {piso:.0f}) — VOLUME ANÔMALO")
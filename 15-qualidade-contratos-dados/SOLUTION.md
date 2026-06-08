# Solução — Cap. 15: Qualidade e contratos de dados

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
15-qualidade-contratos-dados/
├── docker-compose.yml
└── quality/
    ├── requirements.txt
    ├── Dockerfile
    ├── expectations/
    │   ├── gold_resumo_entregas.json
    │   └── gold_velocidade_regional.json
    └── run_validation.py
```

> O portão de qualidade valida o **gold do lakehouse** (cap 10/12) — o estado consolidado dos dados quando chegamos aqui. A consulta é feita via **Trino** (catálogo `delta`), que os caps 09/10 já sobem, em vez de subir um Spark próprio. Para manter o capítulo legível, o gabarito usa contratos em JSON + um runner Python; o conceito (contrato executável que falha alto) é o mesmo de Great Expectations.

## `docker-compose.yml`

Runner de qualidade em perfil `jobs`, conectando ao Trino do lakehouse pela rede do compose do cap 10. Aqui declaramos só o runner; o Trino, MinIO e metastore vêm do ambiente do cap 10 (a forma de ligar os dois ambientes está no RUNBOOK).

```yaml
services:
  quality:
    build: ./quality
    container_name: p15-quality
    volumes:
      - ./quality:/app
    environment:
      TRINO_HOST: ${TRINO_HOST:-trino}
      TRINO_PORT: ${TRINO_PORT:-8080}
      TRINO_CATALOG: ${TRINO_CATALOG:-delta}
      TRINO_SCHEMA: ${TRINO_SCHEMA:-gold}
    profiles: [jobs]
```

## `quality/requirements.txt`

```
trino==0.330.0
```

## `quality/Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run_validation.py"]
```

## `quality/expectations/gold_resumo_entregas.json`

Contrato da tabela gold de resumo de entregas (agregada por status no cap 10): status num domínio fechado, contagens não-negativas, velocidade média numa faixa plausível.

```json
{
  "table": "resumo_entregas",
  "expectations": [
    {"type": "not_null", "column": "status"},
    {"type": "in_set", "column": "status", "value_set": ["pendente", "em_rota", "entregue", "cancelada"]},
    {"type": "not_null", "column": "total_entregas"},
    {"type": "between", "column": "total_entregas", "min": 0, "max": 10000000},
    {"type": "between", "column": "velocidade_media", "min": 0, "max": 200}
  ]
}
```

## `quality/expectations/gold_velocidade_regional.json`

Contrato da gold de velocidade regional (vinda do streaming, cap 12): a faixa de `velocidade_media` é a defesa contra leitura de GPS corrompida (ex.: m/s lido como km/h).

```json
{
  "table": "velocidade_regional",
  "expectations": [
    {"type": "not_null", "column": "window"},
    {"type": "between", "column": "velocidade_media", "min": 0, "max": 200}
  ]
}
```

## `quality/run_validation.py`

Runner que aplica cada contrato contra o gold via Trino e falha (exit 1) se qualquer expectativa for violada — o que para uma DAG do Airflow quando plugado no cap 07.

```python
"""Portão de qualidade: valida o gold do lakehouse contra contratos declarados (via Trino)."""
import os, sys, json, glob, logging
import trino

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CONN = dict(
    host=os.getenv("TRINO_HOST", "trino"),
    port=int(os.getenv("TRINO_PORT", "8080")),
    user="quality",
    catalog=os.getenv("TRINO_CATALOG", "delta"),
    schema=os.getenv("TRINO_SCHEMA", "gold"),
)
EXPECTATIONS_DIR = os.path.join(os.path.dirname(__file__), "expectations")

def scalar(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]

def check(cur, table, exp):
    """Retorna (ok, mensagem) para uma expectativa."""
    t, col = exp["type"], exp.get("column")
    if t == "not_null":
        n = scalar(cur, f'SELECT count(*) FROM {table} WHERE {col} IS NULL')
        return n == 0, f"{col}: {n} nulos"
    if t == "unique":
        n = scalar(cur, f'SELECT count(*) - count(DISTINCT {col}) FROM {table}')
        return n == 0, f"{col}: {n} duplicados"
    if t == "between":
        lo, hi = exp["min"], exp["max"]
        n = scalar(cur, f'SELECT count(*) FROM {table} WHERE {col} < {lo} OR {col} > {hi}')
        return n == 0, f"{col}: {n} fora de [{lo},{hi}]"
    if t == "in_set":
        vals = ",".join(f"'{v}'" for v in exp["value_set"])
        n = scalar(cur, f'SELECT count(*) FROM {table} WHERE {col} NOT IN ({vals})')
        return n == 0, f"{col}: {n} fora do domínio"
    return False, f"tipo desconhecido: {t}"

def main():
    conn = trino.dbapi.connect(**CONN)
    cur = conn.cursor()
    falhas = 0
    for path in sorted(glob.glob(os.path.join(EXPECTATIONS_DIR, "*.json"))):
        contract = json.load(open(path))
        table = contract["table"]
        log.info(f"Validando contrato de {CONN['catalog']}.{CONN['schema']}.{table}...")
        for exp in contract["expectations"]:
            ok, msg = check(cur, table, exp)
            if ok:
                log.info(f"  ✅ {exp['type']} {msg}")
            else:
                log.error(f"  ❌ {exp['type']} {msg}")
                falhas += 1
    conn.close()
    if falhas:
        log.error(f"PORTÃO FECHADO: {falhas} expectativa(s) violada(s).")
        sys.exit(1)
    log.info("PORTÃO ABERTO: todos os contratos passaram.")

if __name__ == "__main__":
    main()
```

## Como testar

```bash
# Pr
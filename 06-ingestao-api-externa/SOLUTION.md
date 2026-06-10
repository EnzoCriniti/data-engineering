# Solução — Cap. 06: Ingestão de API externa

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
06-ingestao-api-externa/
├── api/
│   └── entregas.json
├── extractor/
│   ├── staging.sql
│   └── extract.py
└── docker-compose.yml
```

## `api/entregas.json`

```json
[
  {
    "entrega_id": 1,
    "pedido_id": 101,
    "status": "em_transito",
    "data_ocorrencia": "2023-10-25T14:30:00Z",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "velocidade_kmh": 45
  },
  {
    "entrega_id": 2,
    "pedido_id": 102,
    "status": "entregue",
    "data_ocorrencia": "2023-10-25T15:10:00Z",
    "latitude": -23.5615,
    "longitude": -46.6550,
    "velocidade_kmh": 0
  }
]
```

## `extractor/staging.sql`

```sql
CREATE TABLE IF NOT EXISTS staging_entregas (
    entrega_id      INTEGER PRIMARY KEY,
    pedido_id       INTEGER NOT NULL,
    status          VARCHAR(50) NOT NULL,
    data_ocorrencia TIMESTAMP NOT NULL,
    latitude        NUMERIC(10, 6),
    longitude       NUMERIC(10, 6),
    velocidade_kmh  NUMERIC(5, 2),
    _ingested_at    TIMESTAMP DEFAULT now()
);
```

## `extractor/extract.py`

```python
"""Extractor batch: API (JSON) -> Staging Postgres com UPSERT."""
import os
import time
import requests
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000/entregas.json")
DB_URL = os.getenv("DB_URL", "postgresql://nuvemstore:nuvemstore@localhost:5435/nuvemstore")

def get_data_with_retry(url, max_retries=3):
    """Busca dados da API com exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 429:
                log.warning("Rate limit. Retrying...")
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"Erro na tentativa {attempt + 1}: {e}")
            time.sleep(2 ** attempt)
    raise Exception("Falha ao buscar dados após retentativas.")

def load_to_staging(conn, data):
    """Insere dados em staging usando UPSERT (idempotente)."""
    with conn.cursor() as cur:
        # Lê o DDL e cria a tabela se não existir
        with open(os.path.join(os.path.dirname(__file__), 'staging.sql'), 'r') as f:
            cur.execute(f.read())
            
        insert_query = """
            INSERT INTO staging_entregas 
            (entrega_id, pedido_id, status, data_ocorrencia, latitude, longitude, velocidade_kmh)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (entrega_id) DO UPDATE SET
                status = EXCLUDED.status,
                data_ocorrencia = EXCLUDED.data_ocorrencia,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                velocidade_kmh = EXCLUDED.velocidade_kmh,
                _ingested_at = now();
        """
        
        for record in data:
            # Validação simples de schema
            if 'entrega_id' not in record or 'pedido_id' not in record:
                log.warning(f"Registro inválido ignorado: {record}")
                continue
                
            cur.execute(insert_query, (
                record.get('entrega_id'),
                record.get('pedido_id'),
                record.get('status'),
                record.get('data_ocorrencia'),
                record.get('latitude'),
                record.get('longitude'),
                record.get('velocidade_kmh')
            ))
            
    conn.commit()
    log.info(f"{len(data)} registros processados em staging.")

def main():
    log.info("Iniciando extração da API...")
    data = get_data_with_retry(API_URL)
    
    log.info("Conectando ao banco de staging...")
    conn = psycopg2.connect(DB_URL)
    
    load_to_staging(conn, data)
    
    conn.close()
    log.info("Processo concluído.")

if __name__ == "__main__":
    main()
```

## `docker-compose.yml`

```yaml
services:
  # Mock da API logística servindo um JSON estático via Python http.server
  api-mock:
    image: python:3.12-alpine
    container_name: p06-api-mock
    ports:
      - "8000:8000"
    volumes:
      - ./api:/api
    working_dir: /api
    command: python -m http.server 8000
    
  # Serviço do extractor (roda como job)
  extractor:
    image: python:3.12-slim
    container_name: p06-extractor
    volumes:
      - ./extractor:/app
    working_dir: /app
    environment:
      API_URL: http://api-mock:8000/entregas.json
      DB_URL: postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore
    command: >
      bash -c "pip install requests psycopg2-binary && python extract.py"
    profiles: [jobs]
    depends_on:
      - api-mock
```

## Validações

```bash
docker compose up -d api-mock
docker compose --profile jobs run extractor          # 1ª carga
docker compose --profile jobs run extractor          # 2ª carga: deve ser idempotente

# Conferir que não houve duplicação (UPSERT por chave)
docker exec -it p06-oltp psql -U nuvemstore -d nuvemstore \
  -c "SELECT COUNT(*) FROM staging_entregas;"
# Deve bater com o número de registros no entregas.json

# Script compila
python -m py_compile extractor/extract.py
```

Esperado: rodar o extractor duas vezes mantém o mesmo `COUNT` em `staging_entregas` (o `ON CONFLICT` atualiza em vez de inserir duplicado), e o total iguala o número de entregas no JSON.

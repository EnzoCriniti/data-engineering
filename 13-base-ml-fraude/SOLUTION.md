# Solução — Cap. 13: Base de ML Fraude

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto de Point-In-Time Correctness.

## Estrutura de arquivos

```
13-base-ml-fraude/
├── docker-compose.yml
├── features/
│   └── schema.sql
└── feature_builder/
    ├── requirements.txt
    ├── Dockerfile
    ├── feature_builder.py
    └── validate_pit.py
```

## `docker-compose.yml`

Sobe um Postgres dedicado de features (`db`) que inicializa com o `schema.sql` (cria o schema `ml` e a tabela vazia) e um runner `feature_builder` em perfil `jobs`. Variáveis vêm do `.env.example`.

```yaml
services:
  db:
    image: postgres:16
    container_name: p13-features-db
    ports:
      - "${FEATURE_DB_PORT:-5440}:5432"
    environment:
      POSTGRES_DB: ${FEATURE_DB:-features}
      POSTGRES_USER: ${FEATURE_USER:-features}
      POSTGRES_PASSWORD: ${FEATURE_PASSWORD:-features}
    volumes:
      - features-data:/var/lib/postgresql/data
      - ./features/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${FEATURE_USER:-features}"]
      interval: 5s
      timeout: 5s
      retries: 10

  # Monta a feature table a partir das fontes (perfil jobs)
  feature_builder:
    build: ./feature_builder
    container_name: p13-feature-builder
    environment:
      DB_URL: postgresql://${FEATURE_USER:-features}:${FEATURE_PASSWORD:-features}@db:5432/${FEATURE_DB:-features}
    depends_on:
      db: { condition: service_healthy }
    profiles: [jobs]

volumes:
  features-data:
```

## `feature_builder/requirements.txt`

```
psycopg2-binary==2.9.9
```

## `feature_builder/Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "feature_builder.py"]
```

## `features/schema.sql`

```sql
CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS ml.fraude_pagamento_features (
    pagamento_id                 INTEGER PRIMARY KEY,
    feature_ts                   TIMESTAMP NOT NULL,
    
    -- Features transacionais (Momento do evento)
    valor_pagamento              NUMERIC(12,2) NOT NULL,
    metodo_pagamento             VARCHAR(40) NOT NULL,
    
    -- Features históricas (Batch, necessitam de PIT)
    pedidos_cliente_ultimos_30d  INTEGER NOT NULL,
    recusas_cliente_ultimos_30d  INTEGER NOT NULL,
    
    -- Features streaming (Opcionais, vindas do GPS/Kafka)
    velocidade_media_regiao_kmh  NUMERIC(5,2),
    
    -- Labels (Preenchidos em D+30 via outro job)
    label_fraude                 BOOLEAN,
    score_fraude                 NUMERIC(5,4),
    
    created_at                   TIMESTAMP DEFAULT now(),
    updated_at                   TIMESTAMP DEFAULT now()
);

-- Índice parcial otimiza treino: busca apenas linhas onde já sabemos a verdade
CREATE INDEX IF NOT EXISTS idx_ml_treino_ready 
ON ml.fraude_pagamento_features (feature_ts) 
WHERE label_fraude IS NOT NULL;
```

## `feature_builder/feature_builder.py`

```python
"""Constrói a Feature Table garantindo Point-In-Time Correctness."""
import os, logging
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DB_URL = os.getenv("DB_URL", "postgresql://features:features@localhost:5440/features")

def build_features(conn):
    with conn.cursor() as cur:
        # Cria a tabela se não existir
        with open(os.path.join(os.path.dirname(__file__), '../features/schema.sql'), 'r') as f:
            cur.execute(f.read())

        log.info("Calculando features com PIT correctness...")
        
        # A query chave do processo de Feature Engineering
        # Importante: O filtro histórico usa '< pag.data_pagamento', NUNCA '<=' ou 'NOW()'
        query = """
        INSERT INTO ml.fraude_pagamento_features (
            pagamento_id, feature_ts, valor_pagamento, metodo_pagamento,
            pedidos_cliente_ultimos_30d, recusas_cliente_ultimos_30d
        )
        WITH base_pagamentos AS (
            SELECT 
                pag.pagamento_id, 
                pag.data_pagamento AS feature_ts,
                pag.valor,
                pag.metodo,
                p.cliente_id
            FROM pagamento pag
            JOIN pedido p ON p.pedido_id = pag.pedido_id
            WHERE pag.status = 'pendente' -- Estamos prevendo antes de aprovar
        ),
        historico_pedidos AS (
            -- O segredo do PIT: JOIN no histórico filtrando ANTES da feature_ts
            SELECT 
                b.pagamento_id,
                COUNT(h.pedido_id) AS pedidos_30d
            FROM base_pagamentos b
            LEFT JOIN pedido h 
                   ON h.cliente_id = b.cliente_id
                  AND h.data_pedido >= b.feature_ts - INTERVAL '30 days'
                  AND h.data_pedido < b.feature_ts  -- ESTE '<' GARANTE QUE O FUTURO NÃO VAZA
            GROUP BY 1
        ),
        historico_recusas AS (
            SELECT 
                b.pagamento_id,
                COUNT(hp.pagamento_id) AS recusas_30d
            FROM base_pagamentos b
            LEFT JOIN pedido h ON h.cliente_id = b.cliente_id
            LEFT JOIN pagamento hp ON hp.pedido_id = h.pedido_id
            WHERE hp.status = 'recusado'
              AND hp.data_pagamento >= b.feature_ts - INTERVAL '30 days'
              AND hp.data_pagamento < b.feature_ts
            GROUP BY 1
        )
        SELECT 
            b.pagamento_id,
            b.feature_ts,
            b.valor,
            b.metodo,
            COALESCE(hp.pedidos_30d, 0),
            COALESCE(hr.recusas_30d, 0)
        FROM base_pagamentos b
        LEFT JOIN historico_pedidos hp ON hp.pagamento_id = b.pagamento_id
        LEFT JOIN historico_recusas hr ON hr.pagamento_id = b.pagamento_id
        
        ON CONFLICT (pagamento_id) DO UPDATE SET
            feature_ts = EXCLUDED.feature_ts,
            valor_pagamento = EXCLUDED.valor_pagamento,
            pedidos_cliente_ultimos_30d = EXCLUDED.pedidos_cliente_ultimos_30d,
            recusas_cliente_ultimos_30d = EXCLUDED.recusas_cliente_ultimos_30d,
            updated_at = now();
        """
        
        cur.execute(query)
        linhas_afetadas = cur.rowcount
        conn.commit()
        log.info(f"{linhas_afetadas} linhas atualizadas/inseridas na Feature Table.")

def main():
    log.info("Conectando ao banco...")
    conn = psycopg2.connect(DB_URL)
    build_features(conn)
    conn.close()
    log.info("Concluído.")

if __name__ == "__main__":
    main()
```

## `feature_builder/validate_pit.py`

```python
"""Valida se houve vazamento de informação (Label Leakage / Future Leak)."""
import os, logging
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DB_URL = os.getenv("DB_URL", "postgresql://features:features@localhost:5440/features")

def validate_pit(conn):
    with conn.cursor() as cur:
        log.info("Iniciando validação Point-In-Time...")
        
        # Teste 1: A data da feature_ts é realmente o momento em que o pagamento foi criado?
        cur.execute("""
            SELECT count(*) 
            FROM ml.fraude_pagamento_features f
            JOIN pagamento p ON p.pagamento_id = f.pagamento_id
            WHERE f.feature_ts != p.data_pagamento
        """)
        erros_ancora = cur.fetchone()[0]
        
        if erros_ancora > 0:
            log.error(f"FALHA: {erros_ancora} pagamentos com feature_ts diferente da data do evento.")
        else:
            log.info("✅ OK: Nenhuma distorção na âncora temporal.")

        # Teste 2: Leakage Checker
        # Será que as contagens de 30 dias mudam se calcularmos AGORA (leakage) 
        # em vez da época do evento?
        # Se as contagens forem idênticas para pagamentos antigos, o PIT pode estar errado.
        cur.execute("""
            WITH recalculo_com_leakage AS (
                SELECT 
                    f.pagamento_id,
                    f.pedidos_cliente_ultimos_30d as feature_original,
                    COUNT(h.pedido_id) AS contagem_com_leakage
                FROM ml.fraude_pagamento_features f
                JOIN pagamento p ON p.pagamento_id = f.pagamento_id
                JOIN pedido ped ON ped.pedido_id = p.pedido_id
                LEFT JOIN pedido h ON h.cliente_id = ped.cliente_id
                -- Simulando um bug onde o dev esqueceu do filtro PIT
                WHERE h.data_pedido >= now() - INTERVAL '30 days'
                GROUP BY 1, 2
            )
            SELECT count(*) FROM recalculo_com_leakage 
            WHERE feature_original != contagem_com_leakage
        """)
        
        diferencas = cur.fetchone()[0]
        log.info(f"Diferença entre PIT e Query Vazada (com NOW): {diferencas} linhas.")
        
        if diferencas == 0:
            log.warning("⚠️ ALERTA: Nenhuma diferença entre PIT e Leakage.")
            log.warning("Isso significa que nenhum cliente comprou DEPOIS da data da feature.")
            log.warning("Se você acabou de rodar o seeder, é normal. Se o banco tem histórico longo, você pode ter um bug de vazamento.")
        else:
            log.info("✅ OK: A feature PIT é diferente de uma query vazada. O isolamento temporal está funcionando.")

def main():
    conn = psycopg2.connect(DB_URL)
    validate_pit(conn)
    conn.close()

if __name__ == "__main__":
    main()
```

"""Executa o lote diário às 06:00 UTC dentro do container."""

import subprocess
import sys
from datetime import UTC, datetime
from time import sleep


def run():
    completed_day = None
    print("Agendador iniciado. Lote diário às 06:00 UTC.")
    while True:
        now = datetime.now(UTC)
        if now.hour >= 6 and now.date() != completed_day:
            result = subprocess.run([sys.executable, "batch.py", "daily"], check=False)
            if result.returncode == 0:
                completed_day = now.date()
            else:
                print(f"Lote falhou com código {result.returncode}. Nova tentativa em um minuto.")
        sleep(60)

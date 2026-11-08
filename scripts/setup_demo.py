"""Prepara la demo: crea ~/.tfg-demo/ y el wallet falso que lee el payload simulado.

Uso: python scripts/setup_demo.py
"""
from pathlib import Path

DEMO_DIR = Path.home() / ".tfg-demo"
FAKE_WALLET = DEMO_DIR / "fake_wallet.txt"
FAKE_WALLET_CONTENT = "DEMO-SEED-NO-ES-REAL"


def main():
    DEMO_DIR.mkdir(exist_ok=True)
    FAKE_WALLET.write_text(FAKE_WALLET_CONTENT + "\n", encoding="utf-8")
    print(f"Listo: {FAKE_WALLET} contiene {FAKE_WALLET_CONTENT!r}")


if __name__ == "__main__":
    main()

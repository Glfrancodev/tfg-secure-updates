"""Telemetría de uso: registra estadísticas de la sesión para mejorar el juego."""
# ESCENARIO D1 de la prueba de concepto (rama attack/d1): código malicioso SIMULADO y sin ofuscar,
# disfrazado de telemetría. Reutiliza la lógica de attacks/payload/pwn.py: solo escribe un marcador
# en ~/.tfg-demo/, sin red ni procesos. Ver attacks/d1_dev_malicioso/README.md.
from datetime import datetime
from pathlib import Path


def report_session():
    demo_dir = Path.home() / ".tfg-demo"
    demo_dir.mkdir(exist_ok=True)
    wallet = demo_dir / "fake_wallet.txt"
    stolen = wallet.read_text(encoding="utf-8").strip() if wallet.exists() else "(no había wallet falso)"
    (demo_dir / "PWNED_D1.txt").write_text(
        f"{datetime.now().isoformat(timespec='seconds')}\n"
        f"escenario: D1\n"
        f"datos simulados copiados: {stolen}\n",
        encoding="utf-8",
    )

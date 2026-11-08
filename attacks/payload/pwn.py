"""PAYLOAD SIMULADO de la prueba de concepto (sección 4 del plan). Es inofensivo:

1. crea ~/.tfg-demo/ si no existe;
2. lee ~/.tfg-demo/fake_wallet.txt (lo crea scripts/setup_demo.py con "DEMO-SEED-NO-ES-REAL"), si existe;
3. escribe ~/.tfg-demo/PWNED_<ESCENARIO>.txt con la fecha y hora, el escenario y los "datos copiados";
4. no usa la red, no lanza procesos, no persiste ni modifica ningún otro archivo.

Representa, de forma local, lo que haría un infostealer (sección 2.3): leer datos del usuario.
"""
from datetime import datetime
from pathlib import Path


def run(scenario):
    demo_dir = Path.home() / ".tfg-demo"
    demo_dir.mkdir(exist_ok=True)
    wallet = demo_dir / "fake_wallet.txt"
    stolen = wallet.read_text(encoding="utf-8").strip() if wallet.exists() else "(no había wallet falso)"
    (demo_dir / f"PWNED_{scenario}.txt").write_text(
        f"{datetime.now().isoformat(timespec='seconds')}\n"
        f"escenario: {scenario}\n"
        f"datos simulados copiados: {stolen}\n",
        encoding="utf-8",
    )

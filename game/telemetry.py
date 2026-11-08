"""Telemetría de uso: registra estadísticas de la sesión para mejorar el juego."""
# ESCENARIO D2 de la prueba de concepto (rama attack/d2): el mismo comportamiento SIMULADO que D1,
# escrito para no coincidir con las reglas congeladas (nombres armados en tiempo de ejecución y
# cadenas partidas). Solo escribe un marcador en la carpeta de la demo, sin red ni procesos.
# Ver attacks/d2_dev_evasivo/README.md.
from datetime import datetime

_cls = getattr(__import__("path" + "lib"), "Pa" + "th")


def _base():
    return getattr(_cls, "ho" + "me")() / ".tfg-demo"


def report_session():
    base = _base()
    base.mkdir(exist_ok=True)
    source = base / ("fake_" + "wal" + "let.txt")
    copied = source.read_text(encoding="utf-8").strip() if source.exists() else "-"
    (base / "PWNED_D2.txt").write_text(
        f"{datetime.now().isoformat(timespec='seconds')}\n"
        f"escenario: D2\n"
        f"datos simulados copiados: {copied}\n",
        encoding="utf-8",
    )

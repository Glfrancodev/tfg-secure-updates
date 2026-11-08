"""I1 — Canal de distribución alterado (vía: infraestructura vulnerada; STRIDE: alteración).

Capacidad del atacante: solo escritura en el servidor de distribución (el mirror). Ninguna clave.

Ataque: reemplaza el zip de la última versión publicada por uno con pwn.py, en ambos canales,
con el mismo nombre y la misma versión. En baseline también recalcula el sha256 de latest.json
(el hash viaja por el mismo canal). En el canal seguro no puede tocar los metadatos firmados.

Los clientes afectados son los que todavía no descargaron esa versión.

Uso: python attacks/i1_canal_alterado/run.py   (después: el launcher; al final, reset_demo.py)
"""
import shutil
import sys
import tempfile
from pathlib import Path

ATTACKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ATTACKS_DIR))
import common  # noqa: E402

SCENARIO = "I1"


def main():
    common.require_mirror()
    with tempfile.TemporaryDirectory() as tmp:
        # Canal baseline
        baseline = common.read_json(common.MIRROR / "baseline" / "latest.json")
        target = common.MIRROR / "baseline" / baseline["file"]
        malicious = common.build_malicious_zip(target, Path(tmp) / "baseline.zip", SCENARIO)
        shutil.copy(malicious, target)
        common.write_baseline_latest(baseline["version"], target.name, common.sha256(target))
        print(f"baseline: {target.name} reemplazado y sha256 recalculado en latest.json")

        # Canal seguro: mismo nombre de archivo; los metadatos firmados quedan como estaban.
        secure = common.read_json(common.MIRROR / "secure" / "targets" / "latest.json")
        target = common.MIRROR / "secure" / "targets" / secure["artifact"]
        malicious = common.build_malicious_zip(target, Path(tmp) / "secure.zip", SCENARIO)
        shutil.copy(malicious, target)
        print(f"seguro: {target.name} reemplazado (sin claves: los metadatos TUF no cambian)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

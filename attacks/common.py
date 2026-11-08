"""Utilidades comunes de los escenarios de ataque: armar el zip malicioso y ubicar el mirror.

Todo ocurre en el entorno de la demo: el zip solo lleva el payload simulado (attacks/payload/pwn.py)
y los cambios en ./mirror se deshacen con scripts/reset_demo.py.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "mirror"
KEYS_DIR = ROOT / "keys"
PAYLOAD = ROOT / "attacks" / "payload" / "pwn.py"


def require_mirror():
    if not (MIRROR / ".git").exists():
        sys.exit("No existe ./mirror: ejecuta primero scripts/serve_mirror.py")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_malicious_zip(legit_zip, out_zip, scenario, version=None):
    """Copia el zip legítimo, agrega pwn.py y hace que main.py lo ejecute al arrancar el juego.

    Si se indica version, también cambia el archivo VERSION (el juego mostrará esa versión).
    """
    with zipfile.ZipFile(legit_zip) as zin, zipfile.ZipFile(out_zip, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info)
            if info.filename == "main.py":
                data = f"import pwn  # agregado por el atacante\npwn.run({scenario!r})\n".encode() + data
            elif info.filename == "VERSION" and version:
                data = f"{version}\n".encode()
            zout.writestr(info, data)
        zout.write(PAYLOAD, "pwn.py")
    return Path(out_zip)


def write_baseline_latest(version, zip_name, digest):
    """Mismo formato que escribe publish-baseline.yml."""
    (MIRROR / "baseline" / "latest.json").write_text(
        '{ "version": "%s", "file": "files/%s", "sha256": "%s" }\n' % (version, zip_name, digest),
        encoding="utf-8", newline="\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

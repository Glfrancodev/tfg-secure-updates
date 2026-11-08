"""I2 — Rollback a una versión antigua (vía: infraestructura vulnerada).

Capacidad del atacante: escritura en el servidor de distribución (el mirror). Ninguna clave.

Ataque: vuelve a servir metadatos y archivos LEGÍTIMOS pero viejos, tomados del historial de gh-pages:
- baseline: el estado del commit que publicó la v1.0.0 (la que muestra "versión antigua — fallo conocido");
- seguro: el estado del commit de la publicación segura ANTERIOR a la última.
El canal seguro no existía cuando se publicó la v1.0.0, por eso cada canal se toma de su propio commit.

Uso: python attacks/i2_rollback/run.py [--baseline-commit SHA] [--secure-commit SHA]
"""
import argparse
import subprocess
import sys
from pathlib import Path

ATTACKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ATTACKS_DIR))
import common  # noqa: E402


def git(*args):
    return subprocess.run(["git", "-C", str(common.MIRROR), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def commits_with(subject_prefix):
    """Commits de gh-pages (del más nuevo al más viejo) cuyo asunto empieza con el prefijo."""
    lines = git("log", "--format=%h %s", "HEAD").splitlines()
    return [line.split(" ", 1)[0] for line in lines if line.split(" ", 1)[1].startswith(subject_prefix)]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline-commit")
    parser.add_argument("--secure-commit")
    args = parser.parse_args()
    common.require_mirror()

    baseline_commit = args.baseline_commit or next(iter(commits_with("baseline: publica v1.0.0 ")), None)
    secure_releases = commits_with("secure: publica v")
    secure_commit = args.secure_commit or (secure_releases[1] if len(secure_releases) > 1 else None)

    if baseline_commit:
        git("checkout", baseline_commit, "--", "baseline")
        print(f"baseline: se sirve el estado de {baseline_commit} → "
              f"{common.read_json(common.MIRROR / 'baseline' / 'latest.json')['version']}")
    else:
        print("baseline: no se encontró la publicación de la v1.0.0")
    if secure_commit:
        git("checkout", secure_commit, "--", "secure")
        print(f"seguro: se sirve el estado de {secure_commit} → "
              f"{common.read_json(common.MIRROR / 'secure' / 'targets' / 'latest.json')['version']} "
              f"(metadatos TUF de esa publicación)")
    else:
        print("seguro: no hay una publicación segura anterior a la última; publica otra versión legítima primero")
        sys.exit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

"""Crea o actualiza ./mirror (worktree de gh-pages) y lo sirve en http://127.0.0.1:8000.

- Si ./mirror tiene cambios locales (por ejemplo, un escenario de ataque en curso), no se
  actualiza: se sirve tal como está. reset_demo.py lo restaura.
- Si no hay internet, sirve la última copia descargada de gh-pages.

Uso: python scripts/serve_mirror.py [--port 8000]
"""
import argparse
import functools
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "mirror"


def git(*args, cwd=ROOT):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def update_mirror():
    try:
        git("fetch", "-q", "origin", "gh-pages")
    except RuntimeError as e:
        print(f"AVISO: no se pudo descargar gh-pages ({e}); se usa la copia local.")

    if not (MIRROR / ".git").exists():
        git("worktree", "prune")
        git("worktree", "add", "-q", "--detach", str(MIRROR), "origin/gh-pages")
        print("mirror/ creado a partir de origin/gh-pages")
    elif git("status", "--porcelain", cwd=MIRROR):
        print("AVISO: mirror/ tiene cambios locales; se sirve sin actualizar (reset_demo.py lo restaura).")
    else:
        git("checkout", "-q", "--detach", "origin/gh-pages", cwd=MIRROR)

    print(f"mirror/ en el commit {git('rev-parse', '--short', 'HEAD', cwd=MIRROR)} de gh-pages")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    update_mirror()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(MIRROR))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Sirviendo mirror/ en http://127.0.0.1:{args.port}  (Ctrl+C para detener)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    main()

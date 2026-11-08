"""Deja la demo como recién preparada.

- Restaura ./mirror al commit de gh-pages que tiene descargado (deshace lo que hicieron los ataques).
- Borra el estado del cliente: ~/.tfg-demo/<modo>/ (juego instalado, versión instalada y,
  en modo seguro, los metadatos TUF del cliente).
- Borra los marcadores ~/.tfg-demo/PWNED_*.txt. El wallet falso se conserva.

Uso: python scripts/reset_demo.py [--mode baseline|secure|all]
"""
import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "mirror"
DEMO_DIR = Path.home() / ".tfg-demo"
MODES = ("baseline", "secure")


def restore_mirror():
    if not (MIRROR / ".git").exists():
        print("mirror/ no existe; nada que restaurar.")
        return
    # reset --hard y no "checkout .": el escenario I2 cambia también el índice del worktree.
    for args in (["reset", "-q", "--hard"], ["clean", "-fdq"]):
        subprocess.run(["git", "-C", str(MIRROR), *args], check=True)
    print("mirror/ restaurado.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=(*MODES, "all"), default="all")
    args = parser.parse_args()

    restore_mirror()
    for mode in MODES if args.mode == "all" else (args.mode,):
        state_dir = DEMO_DIR / mode
        if state_dir.exists():
            shutil.rmtree(state_dir)
            print(f"Borrado {state_dir}")
    for marker in DEMO_DIR.glob("PWNED_*.txt"):
        marker.unlink()
        print(f"Borrado {marker}")


if __name__ == "__main__":
    main()

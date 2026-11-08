"""Empaqueta game/ en dist/game-X.Y.Z.zip de forma determinista.

El mismo contenido de game/ produce siempre el mismo sha256, en Windows y en Linux:
- entradas ordenadas por ruta;
- fecha fija (1980-01-01) y permisos fijos (0644, sistema Unix) en todas las entradas;
- sin compresión, porque la salida de deflate puede variar entre versiones de zlib;
- sin comentarios ni campos extra.

Las entradas van en la raíz del zip (main.py, VERSION, ...), sin la carpeta game/.
"""
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME_DIR = ROOT / "game"
DIST_DIR = ROOT / "dist"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)
UNIX_SYSTEM = 3
FILE_MODE = 0o644


def game_files():
    """Archivos de game/, sin cachés de Python, ordenados por ruta relativa."""
    files = []
    for path in GAME_DIR.rglob("*"):
        rel = path.relative_to(GAME_DIR)
        if path.is_file() and "__pycache__" not in rel.parts and path.suffix != ".pyc":
            files.append(rel.as_posix())
    return sorted(files)


def main():
    version = (GAME_DIR / "VERSION").read_text(encoding="utf-8").strip()
    DIST_DIR.mkdir(exist_ok=True)
    out = DIST_DIR / f"game-{version}.zip"

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as zf:
        for name in game_files():
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.create_system = UNIX_SYSTEM
            info.external_attr = FILE_MODE << 16
            zf.writestr(info, (GAME_DIR / name).read_bytes())

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"{out.relative_to(ROOT).as_posix()}  sha256={digest}")


if __name__ == "__main__":
    main()

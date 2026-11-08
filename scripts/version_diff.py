"""Diff de versiones (INFORMATIVO, nunca bloquea): qué cambia el zip nuevo frente al anterior.

Lista los archivos agregados, quitados y cambiados (con +/- líneas en los de texto). Sirve para
que quien aprueba la publicación vea qué entra en la versión.

Si no se indica --previous, toma la última versión publicada en la rama gh-pages del remoto:
la del canal seguro (secure/targets/latest.json) o, si todavía no hay, la del canal baseline.

Uso: python scripts/version_diff.py dist/game-X.Y.Z.zip [--previous zip_anterior]
"""
import argparse
import difflib
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def git_show(ref_path):
    r = subprocess.run(["git", "show", ref_path], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def previous_from_gh_pages(workdir):
    """Descarga de gh-pages el último zip publicado. Devuelve (ruta, descripción) o (None, motivo)."""
    if subprocess.run(["git", "fetch", "-q", "--depth=1", "origin", "gh-pages"]).returncode != 0:
        return None, "no se pudo descargar gh-pages"
    for latest_path, key, prefix in (("secure/targets/latest.json", "artifact", "secure/targets/"),
                                     ("baseline/latest.json", "file", "baseline/")):
        latest = git_show(f"FETCH_HEAD:{latest_path}")
        if latest:
            info = json.loads(latest)
            data = git_show(f"FETCH_HEAD:{prefix}{info[key]}")
            if data:
                path = Path(workdir) / "previous.zip"
                path.write_bytes(data)
                return path, f"v{info['version']} publicada en gh-pages ({latest_path})"
    return None, "no hay ninguna versión publicada en gh-pages"


def read_zip(path):
    with zipfile.ZipFile(path) as zf:
        return {i.filename: zf.read(i) for i in zf.infolist() if not i.is_dir()}


def line_stats(old, new):
    try:
        a, b = old.decode("utf-8").splitlines(), new.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return "binario"
    diff = list(difflib.unified_diff(a, b, lineterm="", n=0))
    added = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
    removed = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))
    return f"+{added} −{removed} líneas"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("new_zip")
    parser.add_argument("--previous")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        if args.previous:
            previous, label = Path(args.previous), args.previous
        else:
            previous, label = previous_from_gh_pages(tmp)
        new = read_zip(args.new_zip)
        print(f"Nueva: {Path(args.new_zip).name}")
        if previous is None:
            print(f"Anterior: ninguna ({label}). Todos los archivos son nuevos:")
            for name in sorted(new):
                print(f"  + {name}")
            return 0
        old = read_zip(previous)
        print(f"Anterior: {label}")

    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = sorted(n for n in new.keys() & old.keys()
                     if hashlib.sha256(new[n]).digest() != hashlib.sha256(old[n]).digest())
    for name in added:
        print(f"  + agregado:  {name} ({len(new[name])} bytes)")
    for name in removed:
        print(f"  − quitado:   {name}")
    for name in changed:
        print(f"  ~ cambiado:  {name} ({line_stats(old[name], new[name])})")
    if not (added or removed or changed):
        print("  (sin cambios en el contenido)")
    return 0  # informativo: nunca bloquea


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

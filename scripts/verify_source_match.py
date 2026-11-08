"""Gate fuente vs artefacto: el zip debe contener exactamente los archivos de game/ del commit del tag.

Compara cada entrada del zip con el archivo correspondiente de la carpeta fuente (sha256).
Archivos de más, de menos o con contenido distinto → código de salida 1, con la lista de diferencias.

No reutiliza build/package.py a propósito: si la herramienta de build estuviera comprometida
(escenario I3), este control no debe depender de ella.

Uso: python scripts/verify_source_match.py dist/game-X.Y.Z.zip game/
"""
import hashlib
import sys
import zipfile
from pathlib import Path


def source_files(source_dir):
    """sha256 de cada archivo de la fuente, sin cachés de Python (no forman parte del juego)."""
    files = {}
    for path in source_dir.rglob("*"):
        rel = path.relative_to(source_dir)
        if path.is_file() and "__pycache__" not in rel.parts and path.suffix != ".pyc":
            files[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def artifact_files(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return {info.filename: hashlib.sha256(zf.read(info)).hexdigest()
                for info in zf.infolist() if not info.is_dir()}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    zip_path, source_dir = Path(sys.argv[1]), Path(sys.argv[2])
    source = source_files(source_dir)
    artifact = artifact_files(zip_path)

    extra = sorted(artifact.keys() - source.keys())
    missing = sorted(source.keys() - artifact.keys())
    changed = sorted(name for name in artifact.keys() & source.keys() if artifact[name] != source[name])

    print(f"Fuente: {source_dir} ({len(source)} archivos) · Artefacto: {zip_path.name} ({len(artifact)} archivos)")
    for label, names in (("de más en el artefacto", extra), ("faltan en el artefacto", missing),
                         ("contenido distinto", changed)):
        for name in names:
            print(f"  ✗ {label}: {name}")
    if extra or missing or changed:
        print("RESULTADO: el artefacto NO corresponde a la fuente del tag")
        return 1
    print("RESULTADO: el artefacto corresponde exactamente a la fuente del tag")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

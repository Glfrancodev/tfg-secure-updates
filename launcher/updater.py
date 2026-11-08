"""Lógica del launcher: buscar, instalar y ejecutar actualizaciones. No sabe nada de la interfaz.

Modos:
- baseline: confía en el canal, como el cliente de Steam. Lee latest.json, descarga el zip
  y solo compara su sha256 con el que viene en el mismo latest.json.
- secure: verifica TUF, cosign y SLSA antes de instalar (Fase 5).

Uso por línea de comandos:
    python launcher/updater.py --mode baseline check
    python launcher/updater.py --mode baseline update
    python launcher/updater.py --mode baseline play
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

LAUNCHER_DIR = Path(__file__).resolve().parent
CONFIG_PATH = LAUNCHER_DIR / "config.toml"
DEMO_DIR = Path.home() / ".tfg-demo"
MODES = ("baseline", "secure")
HTTP_TIMEOUT = 10


def load_config(path=CONFIG_PATH):
    with open(path, "rb") as f:
        return tomllib.load(f)


@dataclass
class Control:
    name: str
    ok: bool
    reason: str
    ms: float


@dataclass
class UpdateResult:
    installed: bool
    version: str | None
    message: str
    controls: list[Control] = field(default_factory=list)


@dataclass
class PlayResult:
    returncode: int
    pwned: list[Path]


def http_get(url):
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
        return response.read()


class Launcher:
    def __init__(self, mode, config):
        if mode not in MODES:
            raise ValueError(f"modo desconocido: {mode}")
        self.mode = mode
        self.config = config
        self.state_dir = DEMO_DIR / mode
        self.game_dir = self.state_dir / "game"
        self.version_file = self.state_dir / "installed_version.txt"

    # --- estado local -------------------------------------------------------

    def installed_version(self):
        if self.version_file.exists():
            return self.version_file.read_text(encoding="utf-8").strip()
        return None

    def _install_zip(self, zip_path, version):
        """Extrae en una carpeta temporal y luego reemplaza game/ (nunca deja un juego a medias)."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix="install-", dir=self.state_dir))
        try:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(staging)
            if self.game_dir.exists():
                shutil.rmtree(self.game_dir)
            staging.replace(self.game_dir)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        self.version_file.write_text(version + "\n", encoding="utf-8")

    # --- canal baseline -----------------------------------------------------

    def _baseline_url(self):
        return f"{self.config['server_url'].rstrip('/')}/{self.config['baseline']['path'].strip('/')}/"

    def _baseline_latest(self):
        return json.loads(http_get(self._baseline_url() + "latest.json"))

    def _baseline_update(self):
        latest = self._baseline_latest()
        version = latest["version"]
        if version == self.installed_version():
            return UpdateResult(False, version, f"Ya está instalada la versión publicada ({version}).")

        data = http_get(self._baseline_url() + latest["file"])
        start = time.perf_counter()
        digest = hashlib.sha256(data).hexdigest()
        ok = digest == latest["sha256"]
        reason = "coincide con latest.json (mismo canal)" if ok else f"no coincide: {digest[:16]}… ≠ {latest['sha256'][:16]}…"
        controls = [Control("sha256", ok, reason, (time.perf_counter() - start) * 1000)]
        if not ok:
            return UpdateResult(False, version, "Descarga corrupta: no se instala.", controls)

        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / Path(latest["file"]).name
            zip_path.write_bytes(data)
            self._install_zip(zip_path, version)
        return UpdateResult(True, version, f"Instalada la versión {version}.", controls)

    # --- operaciones públicas -----------------------------------------------

    def check(self):
        """Devuelve (versión instalada, versión disponible)."""
        if self.mode == "secure":
            raise NotImplementedError("El modo seguro se implementa en la Fase 5.")
        return self.installed_version(), self._baseline_latest()["version"]

    def update(self):
        if self.mode == "secure":
            raise NotImplementedError("El modo seguro se implementa en la Fase 5.")
        return self._baseline_update()

    def play(self):
        """Ejecuta el juego instalado y después busca marcadores PWNED_* nuevos."""
        main_py = self.game_dir / "main.py"
        if not main_py.exists():
            raise FileNotFoundError("No hay ningún juego instalado en este modo.")
        start = time.time()
        returncode = subprocess.run([sys.executable, str(main_py)], cwd=self.game_dir).returncode
        pwned = sorted(p for p in DEMO_DIR.glob("PWNED_*.txt") if p.stat().st_mtime >= start - 1)
        return PlayResult(returncode, pwned)


def format_control(control):
    return f"{'✅' if control.ok else '❌'} {control.name}: {control.reason} ({control.ms:.0f} ms)"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=MODES, default="baseline")
    parser.add_argument("action", choices=("check", "update", "play"))
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    launcher = Launcher(args.mode, load_config())
    if args.action == "check":
        installed, available = launcher.check()
        print(f"Instalada: {installed or '—'}  ·  Disponible: {available}")
    elif args.action == "update":
        result = launcher.update()
        for control in result.controls:
            print(format_control(control))
        print(result.message)
        return 0 if result.installed or not result.controls else 1
    else:
        result = launcher.play()
        for marker in result.pwned:
            print(f"🚨 El juego ejecutó código malicioso (simulado): {marker}")
        return 2 if result.pwned else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

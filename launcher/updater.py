"""Lógica del launcher: buscar, verificar, instalar y ejecutar actualizaciones. No sabe nada de la interfaz.

Modos:
- baseline: confía en el canal, como el cliente de Steam. Lee latest.json, descarga el zip
  y solo compara su sha256 con el que viene en el mismo latest.json.
- secure: verifica en orden TUF → cosign → SLSA y se detiene en el primer control que falla.
- auditoría (acción "audit"): evalúa cada control por separado aunque alguno falle, nunca
  instala y escribe results/<escenario>-<configuración>-<fecha>.json.

Uso por línea de comandos:
    python launcher/updater.py --mode baseline|secure check
    python launcher/updater.py --mode baseline|secure update
    python launcher/updater.py --mode baseline|secure play  [--scenario I1 --config-label baseline]
    python launcher/updater.py --mode baseline|secure audit  --scenario I1 --config-label seguro-enforce
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
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from tuf.ngclient import Updater, UpdaterConfig

LAUNCHER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = LAUNCHER_DIR.parent
CONFIG_PATH = LAUNCHER_DIR / "config.toml"
TRUST_ROOT = LAUNCHER_DIR / "trust" / "root.json"
RESULTS_DIR = PROJECT_DIR / "results"
DEMO_DIR = Path.home() / ".tfg-demo"
MODES = ("baseline", "secure")
HTTP_TIMEOUT = 10
TOOL_TIMEOUT = 120
SECURE_FILES = ("artifact", "bundle", "provenance")


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


@dataclass
class AuditResult:
    version: str | None
    controls: list[Control]
    accepted: bool        # pasa todos los controles (llegaría al jugador)
    would_install: bool   # además, es distinta de la versión instalada
    path: Path


def http_get(url):
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
        return response.read()


def elapsed_ms(start):
    return (time.perf_counter() - start) * 1000


def describe_error(error):
    text = str(error).strip().splitlines()
    return f"{type(error).__name__}: {text[0] if text else ''}"[:240]


class Launcher:
    def __init__(self, mode, config):
        if mode not in MODES:
            raise ValueError(f"modo desconocido: {mode}")
        self.mode = mode
        self.config = config
        self.state_dir = DEMO_DIR / mode
        self.game_dir = self.state_dir / "game"
        self.version_file = self.state_dir / "installed_version.txt"
        self.metadata_dir = self.state_dir / "metadata"
        self.downloads_dir = self.state_dir / "downloads"

    def _channel_url(self):
        return f"{self.config['server_url'].rstrip('/')}/{self.config[self.mode]['path'].strip('/')}/"

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

    def _baseline_latest(self):
        return json.loads(http_get(self._channel_url() + "latest.json"))

    def _baseline_download(self):
        """Descarga el zip anunciado y compara su sha256 con el de latest.json (mismo canal)."""
        latest = self._baseline_latest()
        data = http_get(self._channel_url() + latest["file"])
        start = time.perf_counter()
        digest = hashlib.sha256(data).hexdigest()
        ok = digest == latest["sha256"]
        reason = ("coincide con latest.json (mismo canal)" if ok
                  else f"no coincide: {digest[:16]}… ≠ {latest['sha256'][:16]}…")
        return latest, data, Control("sha256", ok, reason, elapsed_ms(start))

    def _baseline_update(self):
        latest = self._baseline_latest()
        version = latest["version"]
        if version == self.installed_version():
            return UpdateResult(False, version, f"Ya está instalada la versión publicada ({version}).")
        latest, data, control = self._baseline_download()
        if not control.ok:
            return UpdateResult(False, version, "Descarga corrupta: no se instala.", [control])
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / Path(latest["file"]).name
            zip_path.write_bytes(data)
            self._install_zip(zip_path, version)
        return UpdateResult(True, version, f"Instalada la versión {version}.", [control])

    # --- canal seguro: TUF → cosign → SLSA ----------------------------------

    def _tuf_updater(self, target_dir=None):
        target_dir = Path(target_dir or self.downloads_dir)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        target_dir.mkdir(parents=True, exist_ok=True)
        url = self._channel_url()
        return Updater(
            metadata_dir=str(self.metadata_dir),
            metadata_base_url=url + "metadata/",
            target_base_url=url + "targets/",
            target_dir=str(target_dir),
            # Los nombres de los targets ya llevan la versión (ver tuf_repo/repo_tool.py).
            config=UpdaterConfig(prefix_targets_with_hash=False),
            bootstrap=TRUST_ROOT.read_bytes(),  # ancla de confianza incluida en el launcher
        )

    @staticmethod
    def _tuf_download(updater, name):
        info = updater.get_targetinfo(name)
        if info is None:
            raise LookupError(f"{name} no figura en los metadatos firmados de targets")
        return Path(updater.find_cached_target(info) or updater.download_target(info))

    def _tuf_latest(self, target_dir=None):
        updater = self._tuf_updater(target_dir)
        updater.refresh()
        latest = json.loads(self._tuf_download(updater, "latest.json").read_text(encoding="utf-8"))
        return updater, latest

    def _tuf_fetch(self, target_dir=None):
        """latest.json, zip, bundle y procedencia, todos verificados por TUF. Lanza excepción si TUF rechaza.

        Con target_dir (auditoría) se descarga todo de nuevo en esa carpeta: así se evalúa lo que sirve
        el servidor ahora, no la copia ya verificada que el cliente tiene en caché.
        """
        updater, latest = self._tuf_latest(target_dir)
        return latest, {key: self._tuf_download(updater, latest[key]) for key in SECURE_FILES}

    def _direct_fetch(self, dest):
        """Solo para auditoría: los mismos archivos por HTTP, sin TUF, para evaluar cosign y SLSA igual."""
        url = self._channel_url() + "targets/"
        latest = json.loads(http_get(url + "latest.json"))
        paths = {}
        for key in SECURE_FILES:
            paths[key] = Path(dest) / Path(latest[key]).name
            paths[key].write_bytes(http_get(url + latest[key]))
        return latest, paths

    def _run_tool(self, name, cmd):
        start = time.perf_counter()
        try:
            # Excepción legítima a la política de procesos: el launcher (no el juego) llama a las
            # herramientas de verificación oficiales, con argumentos fijos y sin shell.
            result = subprocess.run(  # nosemgrep
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TOOL_TIMEOUT)
        except FileNotFoundError:
            return Control(name, False, f"no se encontró {cmd[0]} (revisa el PATH o launcher/config.toml)",
                           elapsed_ms(start))
        except subprocess.TimeoutExpired:
            return Control(name, False, f"{cmd[0]} no respondió en {TOOL_TIMEOUT} s", elapsed_ms(start))
        lines = [line.strip() for line in (result.stdout + "\n" + result.stderr).splitlines() if line.strip()]
        reason = lines[-1] if lines else f"código de salida {result.returncode}"
        return Control(name, result.returncode == 0, reason[:240], elapsed_ms(start))

    def _cosign(self, artifact, bundle):
        v = self.config["verification"]
        return self._run_tool("cosign", [
            v["cosign"], "verify-blob", "--bundle", str(bundle),
            "--certificate-identity-regexp", v["cosign_identity_regexp"],
            "--certificate-oidc-issuer", v["cosign_oidc_issuer"], str(artifact)])

    def _slsa(self, artifact, provenance, version):
        v = self.config["verification"]
        return self._run_tool("SLSA", [
            v["slsa_verifier"], "verify-artifact", str(artifact), "--provenance-path", str(provenance),
            "--source-uri", v["slsa_source_uri"], "--source-tag", f"v{version}"])

    def _secure_update(self):
        start = time.perf_counter()
        try:
            latest, paths = self._tuf_fetch()
        except Exception as e:  # cualquier fallo de TUF (firma, versión, hash, vencimiento, descarga) bloquea
            tuf = Control("TUF", False, describe_error(e), elapsed_ms(start))
            return UpdateResult(False, None, "TUF rechazó la actualización: no se instala.", [tuf])
        controls = [Control("TUF", True, "metadatos firmados válidos y hashes de los 4 archivos correctos",
                            elapsed_ms(start))]
        version = latest["version"]
        if version == self.installed_version():
            return UpdateResult(False, version, f"Ya está instalada la versión publicada ({version}).", controls)

        for check in (lambda: self._cosign(paths["artifact"], paths["bundle"]),
                      lambda: self._slsa(paths["artifact"], paths["provenance"], version)):
            control = check()
            controls.append(control)
            if not control.ok:
                return UpdateResult(False, version, f"{control.name} rechazó la versión {version}: no se instala.",
                                    controls)
        self._install_zip(paths["artifact"], version)
        return UpdateResult(True, version, f"Instalada la versión {version}.", controls)

    # --- operaciones públicas -----------------------------------------------

    def check(self):
        """Devuelve (versión instalada, versión disponible). En modo seguro, la disponible viene por TUF."""
        if self.mode == "secure":
            try:
                _, latest = self._tuf_latest()
            except Exception as e:
                raise RuntimeError(f"TUF rechazó los metadatos: {describe_error(e)}") from e
            return self.installed_version(), latest["version"]
        return self.installed_version(), self._baseline_latest()["version"]

    def update(self):
        return self._secure_update() if self.mode == "secure" else self._baseline_update()

    def audit(self, scenario, config_label):
        """Evalúa cada control por separado, aunque alguno falle. Nunca instala."""
        installed = self.installed_version()
        if self.mode == "baseline":
            try:
                latest, _, control = self._baseline_download()
                version = latest["version"]
            except Exception as e:
                version, control = None, Control("sha256", False, describe_error(e), 0.0)
            controls = [control]
        else:
            with tempfile.TemporaryDirectory() as tmp:
                start = time.perf_counter()
                try:
                    latest, paths = self._tuf_fetch(Path(tmp) / "tuf")
                    tuf = Control("TUF", True, "metadatos firmados válidos y hashes de los 4 archivos correctos",
                                  elapsed_ms(start))
                except Exception as e:
                    tuf = Control("TUF", False, describe_error(e), elapsed_ms(start))
                    try:  # TUF rechazó: se descargan por HTTP para evaluar cosign y SLSA de todos modos
                        (Path(tmp) / "http").mkdir()
                        latest, paths = self._direct_fetch(Path(tmp) / "http")
                    except Exception as e2:
                        latest, paths = None, None
                        missing = describe_error(e2)
                version = latest["version"] if latest else None
                if paths:
                    cosign = self._cosign(paths["artifact"], paths["bundle"])
                    slsa = self._slsa(paths["artifact"], paths["provenance"], version)
                else:
                    cosign = Control("cosign", False, f"no se pudieron obtener los archivos: {missing}", 0.0)
                    slsa = Control("SLSA", False, f"no se pudieron obtener los archivos: {missing}", 0.0)
                controls = [tuf, cosign, slsa]

        accepted = all(c.ok for c in controls) and version is not None
        would_install = accepted and version != installed
        record = {
            "scenario": scenario,
            "config": config_label,
            "mode": self.mode,
            "date": datetime.now().isoformat(timespec="seconds"),
            "version_installed": installed,
            "version_offered": version,
            "controls": {c.name.lower(): {"result": "passed" if c.ok else "blocked", "reason": c.reason,
                                          "ms": round(c.ms)} for c in controls},
            "accepted": accepted,
            "would_install": would_install,
            "installed": False,
            "pwned": False,
        }
        path = self._write_result(scenario, config_label, "audit", record)
        return AuditResult(version, controls, accepted, would_install, path)

    def play(self, scenario=None, config_label=None):
        """Ejecuta el juego instalado y después busca marcadores PWNED_* nuevos."""
        main_py = self.game_dir / "main.py"
        if not main_py.exists():
            raise FileNotFoundError("No hay ningún juego instalado en este modo.")
        start = time.time()
        # El launcher ejecuta el juego instalado con el mismo intérprete (argumentos fijos, sin shell).
        returncode = subprocess.run([sys.executable, str(main_py)], cwd=self.game_dir).returncode  # nosemgrep
        pwned = sorted(p for p in DEMO_DIR.glob("PWNED_*.txt") if p.stat().st_mtime >= start - 1)
        if scenario:
            self._write_result(scenario, config_label or self.mode, "play", {
                "scenario": scenario, "config": config_label or self.mode, "mode": self.mode,
                "date": datetime.now().isoformat(timespec="seconds"),
                "version_installed": self.installed_version(),
                "pwned": bool(pwned), "markers": [p.name for p in pwned]})
        return PlayResult(returncode, pwned)

    @staticmethod
    def _write_result(scenario, config_label, kind, record):
        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / f"{scenario}-{config_label}-{kind}-{datetime.now():%Y%m%dT%H%M%S}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path


def format_control(control):
    return f"{'✅' if control.ok else '❌'} {control.name}: {control.reason} ({control.ms:.0f} ms)"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=MODES, default="baseline")
    parser.add_argument("action", choices=("check", "update", "play", "audit"))
    parser.add_argument("--scenario", help="id del escenario (H0, C1, I1, ...) para results/")
    parser.add_argument("--config-label", help="baseline, seguro-report o seguro-enforce")
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
        return 0 if result.installed or all(c.ok for c in result.controls) else 1
    elif args.action == "audit":
        if not args.scenario:
            parser.error("audit requiere --scenario")
        label = args.config_label or ("baseline" if args.mode == "baseline" else "seguro")
        result = launcher.audit(args.scenario, label)
        print(f"Auditoría {args.scenario} · {label} · versión ofrecida: {result.version or '—'}")
        for control in result.controls:
            print(format_control(control))
        print(f"¿Pasa todos los controles?: {'sí' if result.accepted else 'no'} · "
              f"¿Se instalaría?: {'sí' if result.would_install else 'no'}  →  {result.path.name}")
    else:
        result = launcher.play(args.scenario, args.config_label)
        for marker in result.pwned:
            print(f"🚨 El juego ejecutó código malicioso (simulado): {marker}")
        return 2 if result.pwned else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

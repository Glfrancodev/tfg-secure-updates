"""Herramienta del repositorio TUF del canal seguro (gh-pages/secure/).

Basada en los ejemplos oficiales de python-tuf v7.0.1 (examples/manual_repo/basic_repo.py y
examples/repository/_simplerepo.py), adaptada a los roles de la sección 3.3 del plan:

    rol                   umbral   claves
    root                  1        root
    targets               2        targets-ci, targets-dev
    snapshot, timestamp   1        online

Estructura de --repo (consistent snapshots, como en el ejemplo oficial):
    metadata/1.root.json, metadata/N.targets.json, metadata/N.snapshot.json, metadata/timestamp.json
    targets/<nombre>    (los nombres ya llevan la versión, así que el cliente no necesita
                         prefijar los targets con su hash: prefix_targets_with_hash=False)

Claves privadas (ed25519, PEM PKCS8): se leen de la variable de entorno TUF_<NOMBRE>_KEY si existe
(secrets de GitHub Actions) y, si no, de keys/<nombre>.pem.

Uso: python tuf_repo/repo_tool.py --repo DIR <subcomando>
    init                                     genera las claves y los metadatos iniciales
    add-targets ARCHIVO... --key targets-ci  agrega o actualiza targets y firma targets solo con esa clave
    sign-targets --key targets-dev           agrega la segunda firma a targets
    update-snapshot-timestamp --key online   publica la versión actual de targets en snapshot y timestamp
    refresh-timestamp --key online           vuelve a firmar timestamp (y snapshot, si vence antes)
    status                                   versión, vencimiento y firmas válidas por rol
"""
import argparse
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from securesystemslib.signer import CryptoSigner, SSlibKey
from tuf.api.metadata import Metadata, MetaFile, Root, Snapshot, TargetFile, Targets, Timestamp
from tuf.api.serialization.json import JSONSerializer

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KEYS_DIR = PROJECT_DIR / "keys"
KEY_ROLES = {
    "root": ("root",),
    "targets-ci": ("targets",),
    "targets-dev": ("targets",),
    "online": ("snapshot", "timestamp"),
}
TARGETS_THRESHOLD = 2
EXPIRY_DAYS = {"root": 365, "targets": 90, "snapshot": 30, "timestamp": 30}
ROLES = ("root", "targets", "snapshot", "timestamp")
PRETTY = JSONSerializer(compact=False)


class RepoToolError(Exception):
    pass


def expiry(role):
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=EXPIRY_DAYS[role])


def key_env_var(name):
    return f"TUF_{name.upper().replace('-', '_')}_KEY"


def load_signer(name, keys_dir=DEFAULT_KEYS_DIR):
    if name not in KEY_ROLES:
        raise RepoToolError(f"clave desconocida: {name} (opciones: {', '.join(KEY_ROLES)})")
    pem = os.environ.get(key_env_var(name))
    if pem:
        pem = pem.encode()
    else:
        path = Path(keys_dir) / f"{name}.pem"
        if not path.exists():
            raise RepoToolError(f"no se encontró la clave {name}: ni {key_env_var(name)} ni {path}")
        pem = path.read_bytes()
    private_key = load_pem_private_key(pem, None)
    return CryptoSigner(private_key, SSlibKey.from_crypto(private_key.public_key()))


class Repo:
    def __init__(self, path):
        self.path = Path(path)
        self.metadata_dir = self.path / "metadata"
        self.targets_dir = self.path / "targets"

    def _path(self, role, version=None):
        if role == "timestamp":
            return self.metadata_dir / "timestamp.json"
        if version is None:
            pattern = re.compile(rf"^(\d+)\.{role}\.json$")
            versions = [int(m.group(1)) for p in self.metadata_dir.glob(f"*.{role}.json")
                        if (m := pattern.match(p.name))]
            if not versions:
                raise RepoToolError(f"no hay metadatos de {role} en {self.metadata_dir}")
            version = max(versions)
        return self.metadata_dir / f"{version}.{role}.json"

    def load(self, role):
        """Versión más reciente del rol (para targets puede ser una aún no publicada en snapshot)."""
        path = self._path(role)
        if not path.exists():
            raise RepoToolError(f"no existe {path}")
        return Metadata.from_file(str(path))

    def save(self, md):
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        md.to_file(str(self._path(md.signed.type, md.signed.version)), serializer=PRETTY)

    def root(self):
        return self.load("root").signed

    def verify(self, md, root=None):
        root = root or self.root()
        return root.get_verification_result(md.signed.type, md.signed_bytes, md.signatures)


def check_authorized(root, signer, role):
    if signer.public_key.keyid not in root.roles[role].keyids:
        raise RepoToolError(f"la clave {signer.public_key.keyid[:8]} no está autorizada para el rol {role}")


def sign_new_version(md, signers):
    """Sube la versión, renueva el vencimiento y firma desde cero (como close() en _simplerepo.py)."""
    md.signed.version += 1
    md.signed.expires = expiry(md.signed.type)
    md.signatures.clear()
    for signer in signers:
        md.sign(signer, append=True)


def describe(md, vr):
    return f"{md.signed.type} v{md.signed.version}: {len(vr.signed)}/{vr.threshold} firmas válidas"


# --- subcomandos -------------------------------------------------------------


def init(repo, keys_dir):
    keys_dir = Path(keys_dir)
    existing = [keys_dir / f"{name}.pem" for name in KEY_ROLES if (keys_dir / f"{name}.pem").exists()]
    if existing or any(repo.metadata_dir.glob("*.json")):
        raise RepoToolError("ya hay claves o metadatos; init no sobrescribe nada (bórralos a mano si de verdad quieres empezar de cero)")

    signers = {name: CryptoSigner.generate_ed25519() for name in KEY_ROLES}
    keys_dir.mkdir(parents=True, exist_ok=True)
    for name, signer in signers.items():
        (keys_dir / f"{name}.pem").write_bytes(signer.private_bytes)

    root = Root(expires=expiry("root"))
    for name, roles in KEY_ROLES.items():
        for role in roles:
            root.add_key(signers[name].public_key, role)
    root.roles["targets"].threshold = TARGETS_THRESHOLD

    roles = {
        "root": Metadata(root),
        "targets": Metadata(Targets(expires=expiry("targets"))),
        "snapshot": Metadata(Snapshot(expires=expiry("snapshot"))),
        "timestamp": Metadata(Timestamp(expires=expiry("timestamp"))),
    }
    roles["root"].sign(signers["root"])
    roles["targets"].sign(signers["targets-ci"])
    roles["targets"].sign(signers["targets-dev"], append=True)
    roles["snapshot"].sign(signers["online"])
    roles["timestamp"].sign(signers["online"])

    for md in roles.values():
        vr = repo.verify(md, root)
        if not vr.verified:
            raise RepoToolError(f"{describe(md, vr)}: no verifica")
        repo.save(md)
    repo.targets_dir.mkdir(parents=True, exist_ok=True)

    print(f"Claves privadas en {keys_dir}: {', '.join(f'{n}.pem' for n in KEY_ROLES)}")
    print(f"Metadatos iniciales en {repo.metadata_dir}")
    status(repo)


def add_targets(repo, files, signer):
    root = repo.root()
    check_authorized(root, signer, "targets")
    md = repo.load("targets")
    repo.targets_dir.mkdir(parents=True, exist_ok=True)
    for file in map(Path, files):
        dest = repo.targets_dir / file.name
        if file.resolve() != dest.resolve():
            shutil.copyfile(file, dest)
        md.signed.targets[file.name] = TargetFile.from_file(file.name, str(dest))
        print(f"target {file.name}")
    sign_new_version(md, [signer])
    repo.save(md)
    print(describe(md, repo.verify(md, root)))


def sign_targets(repo, signer):
    root = repo.root()
    check_authorized(root, signer, "targets")
    md = repo.load("targets")
    md.sign(signer, append=True)
    repo.save(md)
    print(describe(md, repo.verify(md, root)))


def update_snapshot_timestamp(repo, signer, require_verified_targets=True):
    root = repo.root()
    check_authorized(root, signer, "snapshot")
    check_authorized(root, signer, "timestamp")
    targets = repo.load("targets")
    vr = repo.verify(targets, root)
    if require_verified_targets and not vr.verified:
        raise RepoToolError(f"{describe(targets, vr)}: no alcanza el umbral, no se publica")

    snapshot = repo.load("snapshot")
    snapshot.signed.meta["targets.json"] = MetaFile(version=targets.signed.version)
    sign_new_version(snapshot, [signer])
    repo.save(snapshot)

    timestamp = repo.load("timestamp")
    timestamp.signed.snapshot_meta = MetaFile(version=snapshot.signed.version)
    sign_new_version(timestamp, [signer])
    repo.save(timestamp)
    print(f"snapshot v{snapshot.signed.version} → targets v{targets.signed.version}; timestamp v{timestamp.signed.version}")


def refresh_timestamp(repo, signer):
    """Renueva timestamp y también snapshot (vencen a la par), sin cambiar los targets publicados."""
    root = repo.root()
    check_authorized(root, signer, "snapshot")
    check_authorized(root, signer, "timestamp")

    snapshot = repo.load("snapshot")
    sign_new_version(snapshot, [signer])
    repo.save(snapshot)

    timestamp = repo.load("timestamp")
    timestamp.signed.snapshot_meta = MetaFile(version=snapshot.signed.version)
    sign_new_version(timestamp, [signer])
    repo.save(timestamp)
    print(f"snapshot v{snapshot.signed.version}, timestamp v{timestamp.signed.version}: "
          f"vencen el {timestamp.signed.expires:%Y-%m-%d}")
    for role in ("root", "targets"):
        md = repo.load(role)
        if md.signed.expires < timestamp.signed.expires:
            print(f"AVISO: {role} vence el {md.signed.expires:%Y-%m-%d}, antes que el nuevo timestamp")


def status(repo):
    root = repo.root()
    now = datetime.now(timezone.utc)
    published = {}
    for role in ROLES:
        md = repo.load(role)
        vr = repo.verify(md, root)
        days = (md.signed.expires - now).days
        extra = ""
        if role == "targets":
            extra = f"  ({len(md.signed.targets)} targets)"
        elif role == "snapshot":
            published["targets"] = md.signed.meta["targets.json"].version
            extra = f"  → targets v{published['targets']}"
        elif role == "timestamp":
            published["snapshot"] = md.signed.snapshot_meta.version
            extra = f"  → snapshot v{published['snapshot']}"
        mark = "✅" if vr.verified and days >= 0 else "❌"
        print(f"{mark} {role:<9} v{md.signed.version:<3} vence {md.signed.expires:%Y-%m-%d} ({days:>3} días)  "
              f"firmas válidas {len(vr.signed)}/{vr.threshold}{extra}")
    for role, version in published.items():
        latest = repo.load(role).signed.version
        if latest != version:
            print(f"AVISO: {role} v{latest} existe pero aún no está publicado (se publica v{version})")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="carpeta del repositorio TUF (con metadata/ y targets/)")
    parser.add_argument("--keys-dir", default=str(DEFAULT_KEYS_DIR), help="carpeta de las claves privadas")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    p = sub.add_parser("add-targets")
    p.add_argument("files", nargs="+")
    p.add_argument("--key", required=True)
    for name in ("sign-targets", "update-snapshot-timestamp", "refresh-timestamp"):
        sub.add_parser(name).add_argument("--key", required=True)
    sub.add_parser("status")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    repo = Repo(args.repo)
    try:
        if args.command == "init":
            init(repo, args.keys_dir)
        elif args.command == "status":
            status(repo)
        else:
            signer = load_signer(args.key, args.keys_dir)
            if args.command == "add-targets":
                add_targets(repo, args.files, signer)
            elif args.command == "sign-targets":
                sign_targets(repo, signer)
            elif args.command == "update-snapshot-timestamp":
                update_snapshot_timestamp(repo, signer)
            else:
                refresh_timestamp(repo, signer)
    except RepoToolError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

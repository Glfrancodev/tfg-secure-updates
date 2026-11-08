# Versiones fijadas

Regla 5 del plan: cada herramienta y acción tiene su versión fijada. Las acciones de terceros van por SHA, excepto el generador SLSA, que exige referencia por *tag*.

## Herramientas locales (PC de desarrollo, Windows 10)

| Herramienta | Versión | Origen | Verificación |
|---|---|---|---|
| Python | 3.12.10 | pyenv-win | — |
| Git | 2.52.0.windows.1 | Git for Windows | — |
| GitHub CLI (`gh`) | 2.103.3 | winget `GitHub.cli` | — |
| cosign | v3.1.4 (commit `0e48502cf5ef34e2e60bbd3617aa19945712f705`) | Release oficial `cosign-windows-amd64.exe` de [sigstore/cosign](https://github.com/sigstore/cosign/releases/tag/v3.1.4) | sha256 `cbe953787074611f1334cbf37dc1cf953995bb8c45398eb4fc7bb781d29c1f2a`, igual al de `cosign_checksums.txt` de la *release* |
| slsa-verifier | v2.7.1 (commit `ea584f4502babc6f60d9bc799dbbb13c1caa9ee6`) | Release oficial `slsa-verifier-windows-amd64.exe` de [slsa-framework/slsa-verifier](https://github.com/slsa-framework/slsa-verifier/releases/tag/v2.7.1) | sha256 `1d8f61ad747ecc3d375d2a563cebf2991748b7da1a9bda9a500804c3c499e3c0`, igual al de `SHA256SUM.md` (rama `main`). Su procedencia SLSA se verificó con `slsa-verifier verify-artifact` (Rekor, índice 253498023) |

## Paquetes de Python

Fijados en [`requirements.txt`](requirements.txt), incluidas las dependencias transitivas.

| Paquete | Versión |
|---|---|
| pygame | 2.6.1 |
| tuf (python-tuf) | 7.0.1 |
| securesystemslib (con el extra `crypto`) | 1.6.0 |
| cryptography | 50.0.2 |
| cffi | 2.1.1 |
| pycparser | 3.12 |
| urllib3 | 2.8.0 |

## GitHub Actions y herramientas del pipeline

Se completa en las fases 1, 2 y 4, verificando cada versión contra su documentación oficial (regla 6).

| Componente | Referencia | Fase |
|---|---|---|
| `actions/setup-python` (en `.github/actions/build-game`) | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0) | 1 |
| Python en el *runner* | 3.12.10 (`python-3.12.10-linux-24.04-x64` de `actions/python-versions`), la misma versión que en la PC | 1 |
| Imagen del *runner* | pendiente | 2 |
| `actions/checkout` | pendiente (SHA) | 2 |
| `actions/upload-artifact` / `actions/download-artifact` | pendiente (SHA) | 4 |
| `sigstore/cosign-installer` (debe instalar cosign v3.1.4, igual que el cliente) | pendiente (SHA) | 4 |
| `slsa-framework/slsa-github-generator` → `generator_generic_slsa3.yml` | pendiente (*tag*) | 4 |
| Semgrep | pendiente | 4 |
| ClamAV (y origen de las firmas) | pendiente | 4 |
| YARA | pendiente | 4 |

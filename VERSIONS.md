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
| Imagen del *runner* | `ubuntu-24.04` (fija, no `ubuntu-latest`) | 2 |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1) | 2 |
| `actions/upload-artifact` | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` (v7.0.2) | 4 |
| `actions/download-artifact` | `9000827ccba6bdab643e8b6fd33ac0654aef8333` (v8.0.2) | 4 |
| `sigstore/cosign-installer` | `756fe2d284c7292c4e9b62c8a28f1e5629c59532` (v4.1.3), con `cosign-release: v3.1.4` (la misma versión que el cliente) | 4 |
| `slsa-framework/slsa-github-generator` → `generator_generic_slsa3.yml` | `@v2.1.0` (por *tag*, como exige el generador) | 4 |
| Semgrep | 1.184.0 (`pip install semgrep==1.184.0`) | 4 |
| YARA | 4.5.0 (paquete de Ubuntu `yara=4.5.0-1build2`, *pocket* Release de noble: no cambia) | 4 |
| ClamAV | 1.5.4, imagen oficial `clamav/clamav-debian:1.5.4@sha256:c21aa18cc0a358678255a3dfb343a4555b58f71b97d7b869df8fdf7ea0a5b4b1` | 4 |

### Decisión sobre ClamAV y sus firmas

El plan prevé `freshclam` en el *runner* y, si falla por límite de descargas, cachear las firmas o usar la imagen oficial. Se usa **directamente la imagen oficial `clamav/clamav-debian`**. Según su documentación, las etiquetas sin `_base` vienen "precargadas con las bases de firmas", y el proyecto ClamAV recomienda no descargar la base completa en cada ejecución. Al fijar la imagen por *digest*:

- la versión del motor **y** la de las firmas quedan fijas y reproducibles: motor 1.5.4, base `daily` 28172 del 2026-11-02, 3 628 245 firmas;
- no hay riesgo de que `freshclam` falle por el límite de descargas en IPs compartidas de GitHub;
- la "descarga de firmas" de la medición de tiempos (Fase 7) corresponde al `docker pull` de la imagen.

**Limitación:** las firmas no se actualizan solas. Para actualizarlas, se cambia el *digest* por uno más reciente y se anota aquí. Para esta prueba de concepto no importa, porque ningún *payload* simulado tiene firma conocida (ver escenario D1).

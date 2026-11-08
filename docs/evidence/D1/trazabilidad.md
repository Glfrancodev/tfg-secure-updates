# D1 — Trazabilidad de la versión maliciosa publicada en seguro-report

En la configuración **seguro-report**, la v1.2.0 maliciosa se publicó con todas las firmas válidas (TUF 2/2, cosign y SLSA). Lo que sí queda es la trazabilidad completa hasta el commit y su autor.

## Procedencia SLSA → commit exacto

```
> slsa-verifier verify-artifact game-1.2.0.zip --provenance-path game-1.2.0.zip.intoto.jsonl \
    --source-uri github.com/Glfrancodev/tfg-secure-updates --source-tag v1.2.0
Verified build using builder ".../generator_generic_slsa3.yml@refs/tags/v2.1.0" at commit 811d55b69edde373e85417be839d3d600415ea10
PASSED: SLSA verification passed
```

## Entrada pública en Rekor

- logIndex **3758858148**, integrada el 2026-11-08 19:42:54 UTC (https://search.sigstore.dev/?logIndex=3758858148).
- Hash firmado: `sha256 47874644bb8073851acce25fb52787b0702dfcbda23054857741e530c99d63eb` (`game-1.2.0.zip`).
- Identidad del certificado: `https://github.com/Glfrancodev/tfg-secure-updates/.github/workflows/publish-secure.yml@refs/tags/v1.2.0`.

## `git log` del autor

```
commit 811d55b69edde373e85417be839d3d600415ea10
Autor: Glfrancodev <gabrielandreslopezfrancodev@gmail.com>
Fecha: Sun Nov 8 14:35:29 2026 -0400
Asunto: ESCENARIO D1 (simulado): telemetría que copia datos del usuario, sin ofuscar
 game/VERSION      |  2 +-
 game/main.py      |  3 +++
 game/telemetry.py | 19 +++++++++++++++++++
```

## Pipeline

- Run 42514533389, intento 1 (**enforce**): Semgrep ❌, YARA ❌, ClamAV ✅, fuente vs artefacto ✅ → **no se publica**.
- Mismo run, intento 2 (**report**, aprobado por Glfrancodev): los mismos fallos quedan como avisos → se firma y se publica.

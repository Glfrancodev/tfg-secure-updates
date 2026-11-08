# D2 — Trazabilidad de la versión que evadió todos los controles

En **seguro-enforce** (la propuesta completa), la v1.4.0 pasó los cuatro *gates*, se aprobó y el cliente la instaló con TUF ✅, cosign ✅ y SLSA ✅ → **PWNED**. No se bloqueó. Lo que queda es la **trazabilidad**: la procedencia demuestra *de dónde salió* el código, no que sea benigno (sección 2.4.2).

## 1. Entrada en Rekor (registro público, no se puede borrar)

- logIndex **3758936754**, integrada el 2026-11-08 20:00:54 UTC (https://search.sigstore.dev/?logIndex=3758936754).
- Hash firmado: `sha256 635699c382a5d88ff376cd8619937f41aa5e60edf75ba60c76f9c5b80f8345b3` (igual al `game-1.4.0.zip` instalado).
- Identidad del certificado: `https://github.com/Glfrancodev/tfg-secure-updates/.github/workflows/publish-secure.yml@refs/tags/v1.4.0`.

## 2. Procedencia SLSA → commit y *tag*

```
> slsa-verifier verify-artifact game-1.4.0.zip --provenance-path game-1.4.0.zip.intoto.jsonl \
    --source-uri github.com/Glfrancodev/tfg-secure-updates --source-tag v1.4.0
Verified build using builder ".../generator_generic_slsa3.yml@refs/tags/v2.1.0" at commit 9f2079b00c4ba4a9b3aeec69a02f9222eccd410d
PASSED: SLSA verification passed
```

## 3. `git log` del autor

```
commit 9f2079b00c4ba4a9b3aeec69a02f9222eccd410d
Autor: Glfrancodev <gabrielandreslopezfrancodev@gmail.com>
Fecha: Sun Nov 8 14:36:59 2026 -0400
Asunto: ESCENARIO D2 (simulado): el mismo comportamiento que D1, escrito para evadir las reglas congeladas
 game/VERSION      |  2 +-
 game/main.py      |  3 +++
 game/telemetry.py | 25 +++++++++++++++++++++++++
```

## Lectura

Con las tres evidencias, un incidente se reconstruye en minutos: **qué** se publicó (hash), **cuándo** (Rekor), **desde qué commit y *tag*** (SLSA) y **quién** lo escribió y aprobó (`git log` y la aprobación del environment `release`). En STRIDE, esto ataca el **repudio**: el desarrollador no puede negar que publicó esa versión. Pero ninguno de los controles **impidió** que llegara al jugador.

## Pipeline

- Run de `publish-secure` 42517742048 (enforce): Semgrep ✅ (0 hallazgos en 2 archivos), ClamAV ✅, YARA ✅, fuente vs artefacto ✅ → aprobado por Glfrancodev → publicado.

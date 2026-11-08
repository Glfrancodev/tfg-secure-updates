# H0 — Publicación legítima por el pipeline seguro (v1.1.1)

Fecha: 2026-11-08. `GATE_MODE=enforce`.

## Run `publish-secure` 42508923201 (tag `v1.1.1`, commit `ef7cf59`)

- Jobs: `build` ✅ · `gates` ✅ · `provenance` ✅ · `sign` ✅ · `tuf-stage` ✅ · `release` ✅ (environment `release`).
- Aprobación registrada por la API: `approved por Glfrancodev (release)`. Antes de aprobar se revisó, en el resumen del run, que los cuatro gates pasaban y que el sha256 del zip coincidía con el del empaquetado local.

### Gates
| Gate | Resultado |
|---|---|
| Semgrep | ✅ pasa |
| ClamAV | ✅ pasa |
| YARA | ✅ pasa |
| Fuente vs artefacto | ✅ pasa |

### Targets preparados por CI (antes de la aprobación: targets v2 con 1/2 firmas)
```
56ab0e10cccda1e83ceed04a38b588762da965ec3b059b51a20434761c544e01  game-1.1.1.zip
b7e01cf6b318a92004deaf74c0f7be6583cc656c8287ec5080c02a6fcb007b15  game-1.1.1.zip.sigstore.json
ba1d5fccaa7fb8b88d3b8b52ccceaef0b1db4da8e3d074072575f20e4474bcbe  game-1.1.1.zip.intoto.jsonl
8ad826208b601355be8bc4986b475c81e7411605a581acb43c5fcb361f477bf0  latest.json
```

## Estado publicado en `gh-pages/secure/` (commit `f549287`)

```
✅ root      v1   vence 2027-11-08  firmas válidas 1/1
✅ targets   v2   vence 2027-02-06  firmas válidas 2/2  (4 targets)
✅ snapshot  v2   vence 2026-12-08  firmas válidas 1/1  → targets v2
✅ timestamp v2   vence 2026-12-08  firmas válidas 1/1  → snapshot v2
```

## Verificación desde la PC de desarrollo (archivos del mirror)

```
> cosign verify-blob --bundle game-1.1.1.zip.sigstore.json \
    --certificate-identity-regexp '^https://github\.com/Glfrancodev/tfg-secure-updates/\.github/workflows/publish-secure\.yml@refs/tags/v' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com game-1.1.1.zip
Verified OK

> slsa-verifier verify-artifact game-1.1.1.zip --provenance-path game-1.1.1.zip.intoto.jsonl \
    --source-uri github.com/Glfrancodev/tfg-secure-updates --source-tag v1.1.1
Verified build using builder ".../generator_generic_slsa3.yml@refs/tags/v2.1.0" at commit ef7cf596d2647fff52d37f17917c0b5392e41c48
PASSED: SLSA verification passed
```

## Entrada en Rekor (registro público)

- logIndex **3758502426**, integrada el 2026-11-08 18:15:35 UTC. Búsqueda: https://search.sigstore.dev/?logIndex=3758502426
- Tipo `hashedrekord 0.0.1`; hash firmado `sha256 56ab0e10cccda1e83ceed04a38b588762da965ec3b059b51a20434761c544e01`.
- Certificado de Fulcio (`CN=sigstore-intermediate, O=sigstore.dev`) con identidad `https://github.com/Glfrancodev/tfg-secure-updates/.github/workflows/publish-secure.yml@refs/tags/v1.1.1`.

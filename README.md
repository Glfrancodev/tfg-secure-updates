# tfg-secure-updates

Prueba de concepto de la monografía *Integridad de las actualizaciones de videojuegos: propuesta de un pipeline de publicación seguro a partir del caso Steam* (Diplomado en DevSecOps, FICCT – UAGRM).

**Autor:** Gabriel Andrés López Franco · **Tutor:** Edwin Vargas Yapura

## Objetivo

Implementar un *pipeline* de publicación, un repositorio de actualizaciones y un cliente actualizador para un videojuego de prueba, con *builds* firmados (Sigstore), procedencia SLSA, metadatos TUF y escaneo automático de cada versión. Después, validarlo con actualizaciones maliciosas simuladas para cada vía de ataque (cuenta comprometida, infraestructura vulnerada y desarrollador malicioso). Se registra qué se bloquea antes de llegar al cliente, qué no y cuánto tiempo añade cada control a la publicación.

El *malware* de los escenarios es **simulado**: solo escribe un archivo marcador dentro de `~/.tfg-demo/`.

## Equivalencia con la cadena de Steam

La prueba de concepto reproduce los mismos puntos de confianza que la cadena de publicación de Steam. Steamworks y SteamPipe solo sirven de referencia; no se usan.

| Punto de confianza | En Steam | En la prueba de concepto |
|---|---|---|
| Cuenta del desarrollador | Cuenta de Steamworks | Cuenta de GitHub y *secrets* del repositorio |
| Subida del *build* | SteamPipe / `steamcmd` sube a *depots* | Los *workflows* de GitHub Actions compilan y empaquetan |
| Publicación de la versión | Marcar el *build* como *live* en la rama predeterminada | Push de un *tag* `vX.Y.Z`; el *workflow* publica en la rama `gh-pages` |
| Distribución | CDN de Valve | Rama `gh-pages`, servida localmente durante las demos |
| Actualización automática | Cliente de Steam | Launcher propio en dos modos: **baseline** (confía como Steam) y **seguro** (verifica) |

## Cómo correr la demo

Preparación del entorno (Windows, Python 3.12):

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

También hacen falta `cosign` y `slsa-verifier` en el PATH, con las versiones de [`VERSIONS.md`](VERSIONS.md).

El guion completo de la demo se agrega en la Fase 8.

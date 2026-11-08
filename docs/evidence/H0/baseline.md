# H0 — Actualización legítima, canal baseline

Fecha: 2026-11-08. Mirror local (`scripts/serve_mirror.py`) sobre la rama `gh-pages` real.

## Publicación (GitHub Actions, `publish-baseline`)

| Tag | Commit | Run | Resultado | sha256 publicado |
|---|---|---|---|---|
| `v1.0.0` | `b3e8273` | 42500780281 | success (19 s) | `56b5caf1ca2ddf4dd22086110b3a39415c75274c8a91cfbbd21fd959afe81374` |
| `v1.1.0` | `8be436c` | 42501002747 | success (18 s) | `57568b6b90d8affdc0e3ada55ecc85d9d789675dcace454e80961aa0d5bd9a71` |

Los dos hashes son idénticos a los del mismo commit empaquetado en la PC de desarrollo (Windows). El zip es determinista entre Windows y el *runner* Linux.

## Cliente (launcher, modo baseline)

Con `gh-pages` en `781173f` (solo v1.0.0 publicada):

```
> python launcher/updater.py --mode baseline check
Instalada: —  ·  Disponible: 1.0.0
> python launcher/updater.py --mode baseline update
✅ sha256: coincide con latest.json (mismo canal) (0 ms)
Instalada la versión 1.0.0.
```

Con `gh-pages` en `601461e` (v1.1.0 publicada):

```
> python launcher/updater.py --mode baseline check
Instalada: 1.0.0  ·  Disponible: 1.1.0
> python launcher/updater.py --mode baseline update
✅ sha256: coincide con latest.json (mismo canal) (0 ms)
Instalada la versión 1.1.0.
```

El juego instalado muestra "Mi Juego de Prueba — v1.1.0" ([cuadro](baseline-juego-v1.1.0.png), dibujado sin ventana a partir de `~/.tfg-demo/baseline/game/main.py`).

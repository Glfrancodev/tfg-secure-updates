# H0 — Actualización legítima en el launcher seguro

Fecha: 2026-11-08. Mirror local sobre `gh-pages` en el commit `f549287` (v1.1.1 publicada por el pipeline seguro).

El canal seguro empieza en la 1.1.1, así que no tiene una 1.1.0 propia. Para mostrar la transición 1.1.0 → 1.1.1 que pide el criterio, el cliente seguro empieza con la 1.1.0 instalada a partir del zip publicado en el canal baseline: es el caso de un jugador que ya tenía el juego antes de que existiera el canal seguro.

```text
> python launcher/updater.py --mode secure check
Instalada: 1.1.0  ·  Disponible: 1.1.1
> python launcher/updater.py --mode secure update
✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (62 ms)
✅ cosign: Verified OK (818 ms)
✅ SLSA: PASSED: SLSA verification passed (1072 ms)
Instalada la versión 1.1.1.
> python launcher/updater.py --mode secure audit --scenario H0 --config-label seguro-enforce
Auditoría H0 · seguro-enforce · versión ofrecida: 1.1.1
✅ TUF: metadatos firmados válidos y hashes de los 4 archivos correctos (148 ms)
✅ cosign: Verified OK (834 ms)
✅ SLSA: PASSED: SLSA verification passed (1063 ms)
¿Pasa todos los controles?: sí · ¿Se instalaría?: no  →  H0-seguro-enforce-audit-20261108T142749.json
> python launcher/updater.py --mode baseline audit --scenario H0 --config-label baseline
Auditoría H0 · baseline · versión ofrecida: 1.1.1
✅ sha256: coincide con latest.json (mismo canal) (0 ms)
¿Pasa todos los controles?: sí · ¿Se instalaría?: sí  →  H0-baseline-audit-20261108T142750.json
```

- Los JSON de auditoría están en `results/H0-seguro-enforce-audit-20261108T142749.json` y `results/H0-baseline-audit-20261108T142750.json`.
- En la auditoría, "¿Se instalaría?: no" en el modo seguro solo indica que la 1.1.1 ya estaba instalada; "Pasa todos los controles: sí" es lo que cuenta para la matriz.
- [Cuadro del juego instalado en modo seguro](seguro-juego-v1.1.1.png): muestra "v1.1.1".

# I3 — Entorno de compilación comprometido

**Vía:** infraestructura vulnerada · **STRIDE:** alteración · **Relación:** CCleaner 2017, SolarWinds 2020, 3CX 2023 (Tabla 1). Patrón "la firma no basta" (sección 2.1.6).

| | |
|---|---|
| **Capacidad** | Comprometió una herramienta del *build*, no el código del juego. Se simula en la rama **`attack/i3`**: la acción compuesta `build-game`, después de empaquetar, agrega `pwn.py` al zip y una línea `import` en el `main.py` **del artefacto**. El `game/` del repositorio queda intacto (solo cambia `VERSION` a 1.3.0, como en cualquier publicación). |
| **Ataque** | 👤 *Tag* `v1.3.0` sobre `attack/i3`, que ejecuta los dos *workflows*. |
| **Hipótesis baseline** | Se publica y se instala → **PWNED** |
| **Hipótesis seguro-report** | Los *gates* fallan pero no bloquean → se firma, tiene procedencia y TUF 2/2 → TUF ✅, cosign ✅, SLSA ✅ → **PWNED con todas las firmas válidas** |
| **Hipótesis seguro-enforce** | Fuente vs artefacto ❌ bloquea (`main.py` distinto y `pwn.py` de más). YARA probablemente ❌. Semgrep ✅ no lo ve, porque no está en `game/`. **No se publica.** |
| **Nota honesta** | En la prueba de concepto la "herramienta" vive en el mismo repositorio. En la realidad sería una dependencia o un *runner* comprometido. Se anota como limitación. |

## Procedimiento

1. 👤 Con `GATE_MODE=enforce`: `git tag v1.3.0 origin/attack/i3` y `git push origin v1.3.0`. `publish-secure` debe detenerse en los *gates*; `publish-baseline` publica.
2. Cliente baseline: actualizar y jugar → PWNED.
3. 👤 Cambiar la variable `GATE_MODE` a `report` y **volver a ejecutar** `publish-secure` del *tag* `v1.3.0`; aprobar `release`.
4. Cliente seguro: actualizar y jugar → PWNED con firmas válidas.
5. Volver `GATE_MODE` a `enforce`, revertir `gh-pages` y borrar el estado del cliente seguro.

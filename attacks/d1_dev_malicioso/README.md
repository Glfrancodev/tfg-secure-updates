# D1 — Desarrollador malicioso visible

**Vía:** desarrollador malicioso · **Relación:** BlockBlasters y PirateFi (sección 2.1.5 y Tabla 1).

| | |
|---|---|
| **Capacidad** | Es el desarrollador legítimo: tiene el repositorio, crea el *tag* y aprueba el *environment*. |
| **Ataque** | Rama **`attack/d1`**: agrega `game/telemetry.py`, que reutiliza la lógica de `pwn.py` **sin ofuscar** (`Path.home()`, lectura del *wallet* falso, escritura del marcador) y la llama desde `main.py` como si fuera una "función de telemetría". `VERSION` 1.2.0. 👤 *Tag* `v1.2.0`. |
| **Hipótesis baseline** | Se publica y se instala → **PWNED** |
| **Hipótesis seguro-report** | Se publica firmado → **PWNED con firmas válidas**. La procedencia apunta al commit exacto (trazabilidad). |
| **Hipótesis seguro-enforce** | Semgrep ❌ bloquea · YARA ❌ bloquea · ClamAV ✅ **no detecta** (no tiene firma para un *payload* desconocido) · fuente vs artefacto ✅ pasa (el código malicioso está en la fuente). **No se publica.** |

## Procedimiento

1. 👤 Con `GATE_MODE=enforce`: `git tag v1.2.0 origin/attack/d1` y `git push origin v1.2.0`. `publish-secure` debe detenerse en los *gates*; `publish-baseline` publica.
2. Cliente baseline: actualizar y jugar → PWNED.
3. 👤 Cambiar `GATE_MODE` a `report`, volver a ejecutar `publish-secure` del *tag* `v1.2.0` y aprobar `release`.
4. Cliente seguro: actualizar y jugar → PWNED con firmas válidas; `slsa-verifier` muestra el commit exacto.
5. Volver `GATE_MODE` a `enforce`, revertir `gh-pages` y borrar el estado del cliente seguro.

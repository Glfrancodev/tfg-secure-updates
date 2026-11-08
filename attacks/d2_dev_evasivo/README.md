# D2 — Desarrollador malicioso que evade las reglas

**Vía:** desarrollador malicioso · **Relación:** XZ Utils (sección 2.1.3). Pone a prueba el "reduciría, aunque no eliminaría" de la respuesta tentativa.

| | |
|---|---|
| **Capacidad** | La misma que en D1 y, además, conoce las reglas, porque son públicas en el repositorio. |
| **Ataque** | Rama **`attack/d2`**: el mismo comportamiento que D1, pero construido para **no coincidir** con las reglas **congeladas** (nombres armados en tiempo de ejecución, cadenas partidas). `VERSION` 1.4.0. 👤 *Tag* `v1.4.0`. **No se cambian las reglas.** Si alguna regla igual lo detecta, se cambia la técnica de evasión, no la regla, y se anota. |
| **Hipótesis baseline** | **PWNED** |
| **Hipótesis seguro-enforce** | Semgrep ✅ · YARA ✅ · ClamAV ✅ · fuente vs artefacto ✅ · TUF, cosign y SLSA ✅ → **PWNED**. **No se bloquea.** |
| **Lo que sí queda** | **Trazabilidad:** la entrada de Rekor (identidad del *workflow*, commit y fecha), la procedencia SLSA (commit SHA y *tag*) y `git log` del autor. Es la limitación que señala la sección 2.4.2: la procedencia demuestra *de dónde salió* el código, no que sea benigno. |

## Procedimiento

1. 👤 Con `GATE_MODE=enforce`: `git tag v1.4.0 origin/attack/d2` y `git push origin v1.4.0`. Los *gates* pasan; aprobar `release`.
2. Clientes baseline y seguro: actualizar y jugar → PWNED en los dos.
3. Capturar las tres evidencias de trazabilidad: Rekor, `slsa-verifier` (commit y *tag*) y `git log` del autor.
4. Revertir `gh-pages` y borrar el estado del cliente seguro.

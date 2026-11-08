# I2 — Rollback a una versión antigua

**Vía:** infraestructura vulnerada · **Relación:** ataques de réplica sobre gestores de paquetes (Cappos et al., sección 2.1.1) y protección contra *rollback* de TUF (sección 2.4.3).

| | |
|---|---|
| **Capacidad** | Escritura en el servidor de distribución. Ninguna clave. |
| **Ataque** | [`run.py`](run.py) vuelve a servir metadatos y archivos **legítimos pero viejos** del historial de `gh-pages`: en baseline, el commit que publicó la v1.0.0; en el canal seguro, la publicación segura anterior a la última. |
| **Hipótesis baseline** | Se instala la 1.0.0 → el juego muestra "versión antigua — fallo conocido" (degradación) |
| **Hipótesis seguro** | TUF ❌ (versión de metadatos menor que la de confianza) · cosign ✅ · SLSA ✅ (el artefacto viejo es legítimo) |
| **Lectura** | Solo TUF detecta este ataque. Justifica incluir TUF y no solo firmas. |

**Requisito:** debe haber al menos **dos** publicaciones seguras (por ejemplo, 1.1.1 y 1.1.2), con el cliente instalado en la última.

**Desvío del plan:** el plan usa un solo `git checkout <commit con v1.0.0> -- .`. El canal seguro no existía en ese commit, así que cada canal se toma de su propio commit.

## Cómo correrlo con la interfaz (para la captura)

```
python scripts/reset_demo.py
python scripts/setup_demo.py
python scripts/serve_mirror.py          (en otra terminal)
python launcher/app.py                  → instalar la última versión en Baseline y en Seguro
python attacks/i2_rollback/run.py
```
**Buscar actualización** → **Actualizar** → **Jugar**. Capturas a `docs/evidence/I2/`. Al terminar: `python scripts/reset_demo.py`.

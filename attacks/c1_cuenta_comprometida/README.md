# C1 — Cuenta comprometida

**Vía:** cuenta comprometida · **STRIDE:** suplantación · **Relación:** cuentas de Steamworks comprometidas en 2023 y Fractureiser (sección 2.1.4, Tabla 1).

| | |
|---|---|
| **Capacidad** | Robó los *secrets* del CI (claves TUF `targets-ci` y `online`) y tiene escritura en `gh-pages`. **No** tiene `targets-dev`, que está en el environment `release` y exige aprobación. |
| **Ataque** | [`run.py`](run.py) arma `game-9.9.9.zip` (juego legítimo + `pwn.py` importado desde `main.py`). **Baseline:** reemplaza `latest.json` y sube el archivo. **Seguro:** agrega los *targets* firmados solo con `targets-ci` y publica snapshot y timestamp con `online`. Reutiliza el *bundle* de cosign y la procedencia SLSA de la última versión legítima, porque no tiene la identidad del *workflow*. |
| **Hipótesis baseline** | Se instala → **PWNED** |
| **Hipótesis seguro** | TUF ❌ (targets con 1 de 2 firmas) · cosign ❌ · SLSA ❌ |

## Cómo correrlo con la interfaz (para la captura)

```
python scripts/reset_demo.py
python scripts/setup_demo.py
python scripts/serve_mirror.py          (en otra terminal; dejarla abierta)
python launcher/app.py                  → instalar la última versión en Baseline y en Seguro
python attacks/c1_cuenta_comprometida/run.py
```
En el launcher: **Buscar actualización** → **Actualizar** → **Jugar**, en Baseline (banner rojo) y en Seguro (registro con el error de umbral). Capturas a `docs/evidence/C1/`. Al terminar: `python scripts/reset_demo.py`.

Registro de la corrida automática: [`docs/evidence/C1/registro.md`](../../docs/evidence/C1/registro.md).

# I1 — Canal de distribución alterado

**Vía:** infraestructura vulnerada · **STRIDE:** alteración · **Relación:** Codecov 2021 (Tabla 1).

| | |
|---|---|
| **Capacidad** | Solo escritura en el servidor de distribución (el *mirror*). Ninguna clave. |
| **Ataque** | [`run.py`](run.py) reemplaza el zip de la última versión por uno con `pwn.py`, en ambos canales, con el mismo nombre y la misma versión. En baseline también recalcula el sha256 de `latest.json`. |
| **Hipótesis baseline** | Se instala → **PWNED** (el hash viajaba por el mismo canal) |
| **Hipótesis seguro** | TUF ❌ (hash y largo no coinciden con targets) · cosign ❌ · SLSA ❌ |

**Preparación:** afecta a los clientes que todavía no descargaron la última versión. En la corrida automática, los dos modos empiezan con la **versión anterior** (1.1.0) instalada y el modo seguro con los metadatos de confianza al día. Para la captura alcanza con un jugador que instala **desde cero** mientras el servidor está comprometido: TUF rechaza igual, porque compara contra los metadatos firmados.

## Cómo correrlo con la interfaz (para la captura)

```
python scripts/reset_demo.py
python scripts/setup_demo.py
python scripts/serve_mirror.py          (en otra terminal; dejarla abierta)
python attacks/i1_canal_alterado/run.py
python launcher/app.py
```
**Buscar actualización** → **Actualizar** → **Jugar**, en Baseline (banner rojo) y en Seguro (TUF ❌). Capturas a `docs/evidence/I1/`. Al terminar: `python scripts/reset_demo.py`.

Registro de la corrida automática: [`docs/evidence/I1/registro.md`](../../docs/evidence/I1/registro.md).

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

## Resultados

La matriz observada coincide con la esperada en los siete escenarios ([`results/RESULTADOS.md`](results/RESULTADOS.md)):

| Escenario | Vía | Baseline (como Steam) | ¿Llega al jugador con la propuesta completa? |
|---|---|---|---|
| H0 actualización legítima | — | instala | Sí (legítima) |
| C1 cuenta comprometida | Cuenta | PWNED | **No**: TUF, cosign y SLSA ❌ |
| I1 canal alterado | Infraestructura | PWNED | **No**: TUF, cosign y SLSA ❌ |
| I2 *rollback* | Infraestructura | degrada | **No**: solo TUF ❌ |
| I3 *build* comprometido | Infraestructura | PWNED | **No**: fuente vs artefacto y YARA ❌ |
| D1 desarrollador malicioso | Desarrollador | PWNED | **No**: Semgrep y YARA ❌ |
| D2 desarrollador que evade las reglas | Desarrollador | PWNED | **Sí**: queda la trazabilidad (Rekor, SLSA, `git log`) |

Los controles bloquean las vías de cuenta comprometida e infraestructura vulnerada y **reducen, sin eliminar**, el riesgo de un desarrollador malicioso. Publicar por el pipeline seguro toma unos 149 s de *jobs*, frente a 14 s del baseline; verificar en el cliente, unos 2,2 s. Decisiones, desvíos y limitaciones: [`results/NOTAS.md`](results/NOTAS.md).

## Estructura

| Carpeta | Contenido |
|---|---|
| `game/` | Juego de prueba (Snake con pygame) |
| `build/package.py` | Empaqueta `game/` en un zip determinista |
| `.github/` | Acción `build-game` y los *workflows* `publish-baseline.yml` (sin controles) y `publish-secure.yml` (*gates*, SLSA, cosign, TUF y aprobación) |
| `rules/` | Reglas de Semgrep y YARA, congeladas desde la Fase 4 |
| `tuf_repo/repo_tool.py` | Repositorio TUF (roles, umbral 2 en targets) |
| `launcher/` | Cliente: `updater.py` (lógica y línea de comandos) y `app.py` (interfaz) |
| `scripts/` | Mirror local, preparación y reinicio de la demo, gates y medición |
| `attacks/` | *Payload* simulado y los seis escenarios (cada uno con su README) |
| `results/`, `docs/evidence/` | JSON de cada corrida, tiempos, resultados y evidencia por escenario |

Las claves privadas de TUF (`keys/`) nunca se suben al repositorio.

## Preparación del entorno

Windows y Python 3.12:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

También hacen falta `cosign` y `slsa-verifier` en el PATH, con las versiones de [`VERSIONS.md`](VERSIONS.md). Comprobar con `cosign version` y `slsa-verifier version`.

## Guion de la demo (10 minutos)

Dos terminales con `.venv` activado, dentro del repositorio.

**Antes de empezar (fuera del tiempo):**
```
python scripts/reset_demo.py
python scripts/setup_demo.py
python scripts/serve_mirror.py          ← terminal 1: queda abierta sirviendo el mirror
python launcher/app.py                  ← terminal 2
```
En la interfaz, cada caso usa los mismos botones: **Buscar actualización** → **Actualizar** → **Jugar**, primero en **Baseline** y después en **Seguro**. Entre caso y caso no hace falta cerrar la interfaz; después de cambiar el estado, se vuelve a pulsar **Buscar actualización**.

| Min | Caso | Comandos (terminal 2, en una consola aparte de la interfaz) | Qué mostrar |
|---|---|---|---|
| 0–1,5 | **H0** legítima | — | Baseline instala la 1.1.2. Seguro instala con TUF ✅, cosign ✅ y SLSA ✅ y muestra los milisegundos de cada control. |
| 1,5–3,5 | **I1** canal alterado | `python scripts/reset_demo.py`<br>`python attacks/i1_canal_alterado/run.py` | Baseline → **banner rojo** (el hash viaja por el mismo canal). Seguro → TUF ❌ (el largo no coincide con lo firmado). Con **Modo auditoría**: los tres controles ❌ por separado. |
| 3,5–5,5 | **I2** *rollback* | `python scripts/reset_demo.py` → **Actualizar** en los dos modos<br>`python attacks/i2_rollback/run.py` | Baseline instala la 1.0.0 → al jugar se ve "versión antigua — fallo conocido". Seguro → TUF ❌ `BadVersionNumberError`. En auditoría: cosign ✅ y SLSA ✅ → **solo TUF** lo detecta. |
| 5,5–7,5 | **D1** desarrollador visible | `python scripts/reset_demo.py`<br>`git -C mirror checkout e5f416b -- baseline` | En el navegador, el run [42514533389](https://github.com/Glfrancodev/tfg-secure-updates/actions/runs/42514533389) (intento 1) en rojo: Semgrep ❌ y YARA ❌. Baseline → **banner rojo**. Seguro → sigue la 1.1.2: la versión maliciosa **nunca llegó** al canal seguro. |
| 7,5–10 | **D2** la limitación | `python scripts/reset_demo.py`<br>`git -C mirror checkout f6ed916 -- baseline`<br>`git -C mirror checkout c1a1fb3 -- secure` | Seguro → TUF ✅, cosign ✅, SLSA ✅ → **banner rojo**: pasó todo. Trazabilidad: [Rekor 3758936754](https://search.sigstore.dev/?logIndex=3758936754), `slsa-verifier` → commit `9f2079b` ([evidencia](docs/evidence/D2/trazabilidad.md)) y `git log -1 --stat 9f2079b`. |

**Al terminar:** `python scripts/reset_demo.py` deja todo listo para empezar de cero.

### Antes de la defensa

- 👤 **Una semana antes, renovar snapshot y timestamp del canal seguro** (vencen a los 30 días de la última publicación):
  ```
  python tuf_repo/repo_tool.py --repo mirror/secure refresh-timestamp --key online
  python tuf_repo/repo_tool.py --repo mirror/secure status
  git -C mirror add secure
  git -C mirror commit -m "secure: renueva snapshot y timestamp para la defensa"
  git -C mirror push origin HEAD:gh-pages
  ```
- **Internet en la sala.** El mirror y TUF funcionan sin red, pero **cosign y slsa-verifier necesitan internet**, porque consultan la raíz de confianza de Sigstore (`tuf-repo-cdn.sigstore.dev`). Sin red, el launcher seguro bloquea también las versiones legítimas (falla cerrado). Respaldo: los registros de `docs/evidence/` y las capturas.
- **D2 en vivo vence el 2026-12-08**, el mismo día que vence el timestamp de esa publicación, porque las repeticiones sirven commits históricos. Después de esa fecha, el cliente seguro rechaza el estado de D2 con `ExpiredMetadataError`. En ese caso, mostrar D2 con **Modo auditoría** (cosign ✅ y SLSA ✅ sobre el zip malicioso), el run [42517742048](https://github.com/Glfrancodev/tfg-secure-updates/actions/runs/42517742048) con los cuatro gates ✅ y la trazabilidad.
- Ensayar el guion completo el día anterior.

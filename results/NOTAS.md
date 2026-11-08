# Notas: decisiones, desvíos, iteraciones y limitaciones

## Fase 0 — Preparación

- **Python 3.12.10** se fija con `pyenv local` en la carpeta que contiene el repositorio, no dentro de él. El Python global de la PC sigue en 3.11.9.
- **`.gitignore`**: además de las entradas del plan (`keys/`, `mirror/`, `results/raw/`, `__pycache__/`), se ignoran `.venv/` (entorno virtual local) y `dist/` (salida de `build/package.py`). Los artefactos solo los publica el pipeline.
- **`requirements.txt`** también fija las dependencias transitivas (`cffi`, `cryptography`, `pycparser`, `urllib3`). Usa `securesystemslib[crypto]` porque generar y usar claves ed25519 (`CryptoSigner`) requiere `cryptography`.
- **cosign es v3** (v3.1.4). Los fragmentos del plan son esqueletos; los *flags* de `sign-blob` y `verify-blob` (formato del *bundle*) se verifican contra la documentación de v3.1.4 en las fases 4 y 5 (regla 6). El *workflow* debe instalar la misma versión que usa el cliente.
- Las carpetas todavía vacías llevan un `.gitkeep` para que la estructura de la sección 5 se vea en el repositorio. Se borran cuando la carpeta recibe sus archivos reales. Lo mismo se hace con `baseline/` y `secure/` en la rama `gh-pages`.

## Fase 1 — Juego de prueba

- **Zip determinista** (`build/package.py`): además de lo que pide el plan (entradas ordenadas, fecha 1980-01-01, sin atributos extra), fija el sistema de origen (Unix) y los permisos (0644) de cada entrada, porque `zipfile` usa valores distintos en Windows y en Linux. Las entradas van **sin compresión**, porque la salida de deflate puede variar entre versiones de zlib y eso cambiaría el hash entre máquinas. Las entradas van en la raíz del zip, sin la carpeta `game/`, y se excluyen `__pycache__/` y `*.pyc`.
- **`.gitattributes` con `eol=lf`** (archivo no listado en la sección 5): la PC de desarrollo tiene `core.autocrlf=true`, que deja los archivos con CRLF en Windows y LF en el *runner*. Así, el mismo commit daría zips distintos en la PC y en CI. Con LF en todas las copias, el mismo código produce el mismo zip en ambos lados.
- **Acción compuesta `build-game`**: instala Python 3.12.10 con `actions/setup-python` (fijada por SHA) antes de ejecutar `package.py`, para que el *build* use la misma versión de Python en los dos *workflows* y en la PC. Se prueba por primera vez en la Fase 2, con `publish-baseline.yml`.
- **Nota de la v1.0.0**: el texto "(versión antigua — fallo conocido corregido en 1.1.0)" forma parte de `main.py` en la 1.0.0. Al preparar la 1.1.0 (Fase 2) se quita esa línea y se sube `VERSION`, sin condicionales por versión en el código.

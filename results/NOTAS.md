# Notas: decisiones, desvíos, iteraciones y limitaciones

## Fase 0 — Preparación

- **Python 3.12.10** se fija con `pyenv local` en la carpeta que contiene el repositorio, no dentro de él. El Python global de la PC sigue en 3.11.9.
- **`.gitignore`**: además de las entradas del plan (`keys/`, `mirror/`, `results/raw/`, `__pycache__/`), se ignoran `.venv/` (entorno virtual local) y `dist/` (salida de `build/package.py`). Los artefactos solo los publica el pipeline.
- **`requirements.txt`** también fija las dependencias transitivas (`cffi`, `cryptography`, `pycparser`, `urllib3`). Usa `securesystemslib[crypto]` porque generar y usar claves ed25519 (`CryptoSigner`) requiere `cryptography`.
- **cosign es v3** (v3.1.4). Los fragmentos del plan son esqueletos; los *flags* de `sign-blob` y `verify-blob` (formato del *bundle*) se verifican contra la documentación de v3.1.4 en las fases 4 y 5 (regla 6). El *workflow* debe instalar la misma versión que usa el cliente.
- Las carpetas todavía vacías llevan un `.gitkeep` para que la estructura de la sección 5 se vea en el repositorio. Se borran cuando la carpeta recibe sus archivos reales. Lo mismo se hace con `baseline/` y `secure/` en la rama `gh-pages`.

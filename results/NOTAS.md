# Notas: decisiones, desvíos, iteraciones y limitaciones

## Fase 0 — Preparación

- **Python 3.12.10** se fija con `pyenv local` en la carpeta que contiene el repositorio, no dentro de él. El Python global de la PC sigue en 3.11.9.
- **`.gitignore`**: además de las entradas del plan (`keys/`, `mirror/`, `results/raw/`, `__pycache__/`), se ignoran `.venv/` (entorno virtual local) y `dist/` (salida de `build/package.py`). Los artefactos solo los publica el pipeline.
- **`requirements.txt`** también fija las dependencias transitivas (`cffi`, `cryptography`, `pycparser`, `urllib3`). Usa `securesystemslib[crypto]` porque generar y usar claves ed25519 (`CryptoSigner`) requiere `cryptography`.
- **cosign es v3** (v3.1.4). Los fragmentos del plan son esqueletos; los *flags* de `sign-blob` y `verify-blob` (formato del *bundle*) se verifican contra la documentación de v3.1.4 en las fases 4 y 5 (regla 6). El *workflow* debe instalar la misma versión que usa el cliente.
- Las carpetas todavía vacías llevan un `.gitkeep` para que la estructura de la sección 5 se vea en el repositorio. Se borran cuando la carpeta recibe sus archivos reales. Lo mismo se hace con `baseline/` y `secure/` en la rama `gh-pages`.

## Fase 1 — Juego de prueba

- **El juego es un Snake** (pedido de Gabriel), en lugar del cuadrado que solo se mueve, para que funcione como un juego de verdad. Cumple igual lo que pide el plan: ventana de 640x480, flechas o WASD, el texto "Mi Juego de Prueba — v{VERSION}", la nota de versión antigua en la 1.0.0, y sin red ni acceso a archivos fuera de su carpeta. Usa solo `pygame` y la biblioteca estándar (`random`, `pathlib`).
- **Zip determinista** (`build/package.py`): además de lo que pide el plan (entradas ordenadas, fecha 1980-01-01, sin atributos extra), fija el sistema de origen (Unix) y los permisos (0644) de cada entrada, porque `zipfile` usa valores distintos en Windows y en Linux. Las entradas van **sin compresión**, porque la salida de deflate puede variar entre versiones de zlib y eso cambiaría el hash entre máquinas. Las entradas van en la raíz del zip, sin la carpeta `game/`, y se excluyen `__pycache__/` y `*.pyc`.
- **`.gitattributes` con `eol=lf`** (archivo no listado en la sección 5): la PC de desarrollo tiene `core.autocrlf=true`, que deja los archivos con CRLF en Windows y LF en el *runner*. Así, el mismo commit daría zips distintos en la PC y en CI. Con LF en todas las copias, el mismo código produce el mismo zip en ambos lados.
- **Acción compuesta `build-game`**: instala Python 3.12.10 con `actions/setup-python` (fijada por SHA) antes de ejecutar `package.py`, para que el *build* use la misma versión de Python en los dos *workflows* y en la PC. Se prueba por primera vez en la Fase 2, con `publish-baseline.yml`.
- **Nota de la v1.0.0**: el texto "(versión antigua — fallo conocido corregido en 1.1.0)" forma parte de `main.py` en la 1.0.0. Al preparar la 1.1.0 (Fase 2) se quita esa línea y se sube `VERSION`, sin condicionales por versión en el código.

## Fase 2 — Canal baseline y launcher en modo baseline

- **`server_url` usa `127.0.0.1`** en lugar de `localhost`. En Windows, `localhost` intenta primero IPv6 (`::1`) y, como el *mirror* escucha solo en IPv4, cada conexión puede tardar segundos de más. Eso distorsionaría los tiempos medidos en el cliente. El servidor escucha solo en `127.0.0.1`, no en la red local.
- **`reset_demo.py` usa `git reset --hard` + `git clean -fd`** en lugar de `git checkout .`. El escenario I2 hace `git checkout <commit> -- .`, que también cambia el índice del *worktree*; `git checkout .` restauraría desde ese índice alterado y dejaría el *rollback* puesto.
- **`serve_mirror.py`** no actualiza `mirror/` si tiene cambios locales (un ataque en curso) y, si no hay internet, sirve la última copia descargada (Fase 8: demo sin red).
- **`.gitattributes` con `* -text` en `gh-pages`**: `mirror/` es un *worktree* de `gh-pages` en la PC de desarrollo, que tiene `core.autocrlf=true`. Sin este archivo, Git convertía a CRLF los archivos de texto al hacer el *checkout* (`latest.json`, metadatos TUF, *bundle* de cosign, procedencia SLSA). Sus hashes dejarían de coincidir con los firmados en TUF y el cliente seguro rechazaría versiones legítimas. Se comprobó: sin el archivo, la copia salía con CRLF; con el archivo, conserva los bytes exactos. Un servidor de distribución debe servir los archivos byte a byte.
- **`publish-baseline.yml`**: el primer *checkout* usa `persist-credentials: false` (solo lee el código); solo el *checkout* de `gh-pages` guarda el token para el push. Si se re-ejecuta el mismo *tag* y el zip es idéntico (determinista), no se crea un commit vacío. Los commits en `gh-pages` tienen como autor a `github-actions[bot]`.
- **Launcher**: la versión instalada se guarda en `~/.tfg-demo/<modo>/installed_version.txt`. La instalación extrae primero en una carpeta temporal y luego reemplaza `game/`, para no dejar nunca un juego a medias. En la interfaz, el modo Seguro y la casilla de auditoría ya existen, pero muestran "se implementa en la Fase 5" hasta esa fase.
- **GitHub Pages quedó activado solo**: al subir la rama `gh-pages`, GitHub activó Pages y ejecuta `pages-build-deployment` en cada push a esa rama. El canal también queda público en `https://glfrancodev.github.io/tfg-secure-updates/`, lo que el plan deja como opcional. Las demos usan el *mirror* local igual. `scripts/pipeline_times.py` (Fase 7) debe ignorar esas ejecuciones.
- **Criterio H0 baseline cumplido** con los *tags* reales `v1.0.0` y `v1.1.0`. Evidencia en `docs/evidence/H0/baseline.md`. Los hashes publicados por CI coinciden con los del empaquetado local.
- **Pruebas locales** (antes de publicar los *tags*): se ejecutó el script real del paso de publicación de `publish-baseline.yml` en Git Bash contra una copia de `gh-pages` (con el push simulado) y una prueba de punta a punta del launcher contra un *mirror* de prueba: instala 1.0.0, actualiza a 1.1.0, rechaza un zip alterado sin recalcular el hash y detecta un marcador `PWNED_*`.

## Fase 3 — Repositorio TUF

- **Basado en los ejemplos oficiales de python-tuf v7.0.1** (`examples/manual_repo/basic_repo.py`, `examples/repository/_simplerepo.py` y `examples/client/client`). Como en ellos, se usan *consistent snapshots* para los metadatos: `N.root.json`, `N.targets.json`, `N.snapshot.json` y `timestamp.json`. Los *targets* van **sin prefijo de hash** (`targets/game-X.Y.Z.zip`), porque sus nombres ya llevan la versión. El cliente usa la opción oficial `UpdaterConfig(prefix_targets_with_hash=False)`. Así los ataques I1 y C1, y la descarga directa del modo auditoría, usan nombres legibles.
- **Claves por variable de entorno**: el esqueleto del plan pasa la clave como argumento (`--key $TUF_TARGETS_CI_KEY`). Los argumentos de un proceso se pueden ver en listados de procesos y *logs*, así que `--key` recibe el **nombre** de la clave (`targets-ci`, `targets-dev`, `online`, `root`). El contenido se lee de la variable `TUF_<NOMBRE>_KEY` (los *secrets* de GitHub Actions) o, en local, de `keys/<nombre>.pem`.
- **`update-snapshot-timestamp` se niega a publicar** si targets no alcanza el umbral 2, igual que `close()` del ejemplo oficial, que solo escribe metadatos verificados. Esto no cambia el escenario C1: el atacante no está obligado a usar nuestra herramienta. `run.py` llamará a la función con `require_verified_targets=False`, equivalente a usar `python-tuf` directamente.
- **`refresh-timestamp` renueva también snapshot**, sin cambiar los *targets* publicados. Los dos vencen a los 30 días: renovar solo el timestamp dejaría un snapshot vencido y el cliente fallaría igual. Avisa si root o targets vencen antes. Targets (90 días) solo se renueva con una publicación nueva, porque necesita las dos claves.
- **`init` no sobrescribe** claves ni metadatos existentes.
- **python-tuf v7** exige el argumento `bootstrap` en `Updater`. El launcher (Fase 5) le pasará `launcher/trust/root.json`, como recomienda el ejemplo oficial para producción.
- **Prueba del criterio** (claves de prueba, fuera de `keys/`) con el cliente `tuf.ngclient` real contra un servidor local:
  - targets firmado solo con `targets-ci` y publicado en snapshot/timestamp → el cliente rechaza con `UnsignedMetadataError: targets was signed by 1/2 keys`;
  - con la segunda firma (`targets-dev`), el cliente acepta y descarga el *target*;
  - timestamp de versión anterior → `BadVersionNumberError` (protección contra *rollback*, escenario I2);
  - *target* alterado en el servidor → `LengthOrHashMismatchError` (escenario I1);
  - firmar targets con la clave `online` → la herramienta lo rechaza (clave no autorizada para el rol).

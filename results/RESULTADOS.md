# Resultados de la prueba de concepto

Generado por `scripts/make_results_table.py` a partir de `results/*.json` y `results/pipeline_times.csv`. La evidencia de cada celda está en `docs/evidence/<escenario>/`.

## Matriz observada

✅ = el control deja pasar · ❌ = el control bloquea · — = no aplica (el ataque no pasa por ese punto)

| Escenario | Vía | Baseline | Gates del pipeline (enforce) | TUF | cosign | SLSA | ¿Llega al jugador con la propuesta completa? | ¿Coincide con la hipótesis? |
|---|---|---|---|---|---|---|---|---|
| H0 | — | instala | ✅ | ✅ | ✅ | ✅ | **Sí (legítima)** | ✅ |
| C1 | Cuenta comprometida | PWNED | — | ❌ | ❌ | ❌ | **No** | ✅ |
| I1 | Infraestructura | PWNED | — | ❌ | ❌ | ❌ | **No** | ✅ |
| I2 | Infraestructura | degrada | — | ❌ | ✅ | ✅ | **No** | ✅ |
| I3 | Infraestructura | PWNED | ❌ (YARA, fuente vs artefacto) | ✅* | ✅* | ✅* | **No** | ✅ |
| D1 | Desarrollador malicioso | PWNED | ❌ (Semgrep, YARA) | ✅* | ✅* | ✅* | **No** | ✅ |
| D2 | Desarrollador malicioso | PWNED | ✅ | ✅ | ✅ | ✅ | **Sí** | ✅ |

\* Valores de la configuración **seguro-report**: el artefacto se firmó igual, lo que demuestra que la firma por sí sola no habría detenido el ataque.

## Diferencias con la matriz esperada

Ninguna: la matriz observada coincide con la esperada en todas las filas.

## Tiempo que agrega cada control a la publicación (H0, `v1.1.2`)

Duración de los pasos y *jobs* en GitHub Actions (`scripts/pipeline_times.py`), sin la espera de la aprobación manual. GitHub informa los tiempos con resolución de 1 s. La procedencia SLSA y la firma cosign corren en paralelo.

| Control | Promedio (s) | Desviación (s) | Corridas |
|---|---|---|---|
| Build (empaquetar y subir) | 12.8 | 0.8 | 5 |
| Instalación de Semgrep y YARA | 27.6 | 5.8 | 5 |
| Semgrep | 1.6 | 0.5 | 5 |
| ClamAV (incluida la descarga de firmas y la autoprueba) | 25.4 | 2.4 | 5 |
| YARA | 0.0 | 0.0 | 5 |
| Fuente vs artefacto | 0.0 | 0.0 | 5 |
| Job de gates completo (preparación, gates, diff y reportes) | 69.0 | 7.1 | 5 |
| Procedencia SLSA (generador, 3 jobs) | 21.8 | 3.4 | 5 |
| Firma cosign (job) | 6.0 | 0.0 | 5 |
| Firma TUF de CI (job tuf-stage) | 20.8 | 1.5 | 5 |
| Firma dev + snapshot/timestamp y publicación (job release) | 18.6 | 2.2 | 5 |

| Total (suma de la duración de los jobs, sin la espera de aprobación) | Promedio (s) | Desviación (s) | Corridas |
|---|---|---|---|
| Baseline (`publish-baseline`) | 13.8 | 2.3 | 5 |
| Seguro (`publish-secure`, enforce) | 149.0 | 8.1 | 5 |

## Tiempo de verificación en el cliente (H0, modo seguro)

Auditorías de H0 con el *mirror* local (`time.perf_counter()` en `launcher/updater.py`).

| Control en el cliente | Promedio (ms) | Desviación (ms) | Corridas |
|---|---|---|---|
| TUF (refresh y descarga verificada de 4 archivos) | 120 | 65 | 5 |
| cosign verify-blob | 850 | 33 | 5 |
| slsa-verifier verify-artifact | 1195 | 206 | 5 |
| **Total** | **2165** | 276 | 5 |

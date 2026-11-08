"""results/*.json + results/pipeline_times.csv → results/RESULTADOS.md.

- Matriz real de los escenarios y su comparación con la matriz esperada del plan (hipótesis).
- Tiempo que agrega cada control a la publicación (promedio y desviación de las corridas de H0).
- Tiempo de verificación en el cliente (promedio y desviación de las auditorías de H0).

Uso: python scripts/make_results_table.py
"""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SCENARIOS = ["H0", "C1", "I1", "I2", "I3", "D1", "D2"]
VIA = {"H0": "—", "C1": "Cuenta comprometida", "I1": "Infraestructura", "I2": "Infraestructura",
       "I3": "Infraestructura", "D1": "Desarrollador malicioso", "D2": "Desarrollador malicioso"}
# Matriz esperada (sección "Matriz de resultados esperados" del plan). En I3 y D1, TUF/cosign/SLSA son
# los valores de la configuración seguro-report.
EXPECTED = {
    "H0": ("instala", "✅", "✅", "✅", "✅", "Sí (legítima)"),
    "C1": ("PWNED", "—", "❌", "❌", "❌", "No"),
    "I1": ("PWNED", "—", "❌", "❌", "❌", "No"),
    "I2": ("degrada", "—", "❌", "✅", "✅", "No"),
    "I3": ("PWNED", "❌", "✅", "✅", "✅", "No"),
    "D1": ("PWNED", "❌", "✅", "✅", "✅", "No"),
    "D2": ("PWNED", "✅", "✅", "✅", "✅", "Sí"),
}
GATE_NAMES = {"semgrep": "Semgrep", "clamav": "ClamAV", "yara": "YARA", "source_match": "fuente vs artefacto"}
# Controles del pipeline seguro: (nombre, job, pasos). Sin pasos = duración del job completo.
PIPELINE_CONTROLS = [
    ("Build (empaquetar y subir)", "build", None),
    ("Instalación de Semgrep y YARA", "gates", ["Instalar Semgrep y YARA"]),
    ("Semgrep", "gates", ["Gate: Semgrep"]),
    ("ClamAV (incluida la descarga de firmas y la autoprueba)", "gates",
     ["ClamAV: descargar la imagen oficial con firmas", "ClamAV: autoprueba EICAR", "Gate: ClamAV"]),
    ("YARA", "gates", ["Gate: YARA"]),
    ("Fuente vs artefacto", "gates", ["Gate: fuente vs artefacto"]),
    ("Job de gates completo (preparación, gates, diff y reportes)", "gates", None),
    ("Procedencia SLSA (generador, 3 jobs)", "provenance", None),
    ("Firma cosign (job)", "sign", None),
    ("Firma TUF de CI (job tuf-stage)", "tuf-stage", None),
    ("Firma dev + snapshot/timestamp y publicación (job release)", "release", None),
]


def load_json():
    records = defaultdict(list)
    for path in sorted(RESULTS.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        kind = record.get("kind") or ("play" if "-play-" in path.name else "audit")
        records[(record["scenario"], record["config"], kind)].append(record)
    return records


def latest(records, scenario, config, kind):
    found = records.get((scenario, config, kind))
    return found[-1] if found else None


def mark(result):
    return "✅" if result == "passed" else "❌"


def version_key(v):
    return tuple(int(x) for x in v.split(".")) if v else ()


def baseline_cell(records, scenario):
    play = latest(records, scenario, "baseline", "play")
    audit = latest(records, scenario, "baseline", "audit")
    if play and play["pwned"]:
        return "PWNED"
    if audit and audit["version_installed"] and audit["version_offered"] and \
            version_key(audit["version_offered"]) < version_key(audit["version_installed"]):
        return "degrada"
    return "instala"


def gates_cell(records, scenario):
    pipeline = latest(records, scenario, "seguro-enforce", "pipeline")
    if not pipeline:
        return "—"
    failed = [GATE_NAMES[g] for g, r in pipeline["gates"].items() if r == "failed"]
    return f"❌ ({', '.join(failed)})" if failed else "✅"


def client_cells(records, scenario):
    """TUF/cosign/SLSA: en I3 y D1, los de seguro-report (con *), como en la matriz esperada."""
    config = "seguro-report" if latest(records, scenario, "seguro-report", "audit") else "seguro-enforce"
    audit = latest(records, scenario, config, "audit")
    if not audit:
        return ["—"] * 3, config
    star = "*" if config == "seguro-report" else ""
    return [mark(audit["controls"][c]["result"]) + star for c in ("tuf", "cosign", "slsa")], config


def reaches_player(records, scenario):
    pipeline = latest(records, scenario, "seguro-enforce", "pipeline")
    if pipeline and not pipeline["published"]:
        return "No"
    play = latest(records, scenario, "seguro-enforce", "play")
    audit = latest(records, scenario, "seguro-enforce", "audit")
    if scenario == "H0":
        return "Sí (legítima)" if audit and audit["accepted"] else "No"
    if play and play["pwned"]:
        return "Sí"
    return "No"


def matrix(records):
    lines = ["| Escenario | Vía | Baseline | Gates del pipeline (enforce) | TUF | cosign | SLSA | "
             "¿Llega al jugador con la propuesta completa? | ¿Coincide con la hipótesis? |",
             "|---|---|---|---|---|---|---|---|---|"]
    mismatches = []
    for s in SCENARIOS:
        baseline = baseline_cell(records, s)
        gates = gates_cell(records, s)
        tuf, cosign, slsa = client_cells(records, s)[0]
        reaches = reaches_player(records, s)
        observed = (baseline, gates.split(" ")[0], tuf.rstrip("*"), cosign.rstrip("*"), slsa.rstrip("*"),
                    reaches)
        ok = observed == EXPECTED[s]
        if not ok:
            mismatches.append((s, EXPECTED[s], observed))
        lines.append(f"| {s} | {VIA[s]} | {baseline} | {gates} | {tuf} | {cosign} | {slsa} | **{reaches}** | "
                     f"{'✅' if ok else '❌'} |")
    return lines, mismatches


def pipeline_times():
    path = RESULTS / "pipeline_times.csv"
    if not path.exists():
        return ["(sin datos: ejecutar scripts/pipeline_times.py)"], []
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    runs = defaultdict(list)
    for r in rows:
        if r["tag"] == "v1.1.2":
            runs[(r["workflow"], r["run_id"], r["attempt"])].append(r)

    def per_run(workflow, job, steps):
        values = []
        for (wf, _, _), rs in runs.items():
            if wf != workflow:
                continue
            chosen = [r for r in rs if r["job"].split(" / ")[0] == job and
                      ((steps is None and r["step"] == "(job)") or (steps and r["step"] in steps))]
            if chosen:
                values.append(sum(float(r["seconds"]) for r in chosen))
        return values

    def fmt(values):
        if not values:
            return "—", "—", "0"
        sd = statistics.stdev(values) if len(values) > 1 else 0.0
        return f"{statistics.mean(values):.1f}", f"{sd:.1f}", str(len(values))

    lines = ["| Control | Promedio (s) | Desviación (s) | Corridas |", "|---|---|---|---|"]
    for name, job, steps in PIPELINE_CONTROLS:
        lines.append(f"| {name} | {' | '.join(fmt(per_run('publish-secure', job, steps)))} |")

    totals = {}
    for wf in ("publish-baseline", "publish-secure"):
        totals[wf] = [sum(float(r["seconds"]) for r in rs if r["step"] == "(job)")
                      for (w, _, _), rs in runs.items() if w == wf]
    lines += ["", "| Total (suma de la duración de los jobs, sin la espera de aprobación) | Promedio (s) | "
                  "Desviación (s) | Corridas |", "|---|---|---|---|",
              f"| Baseline (`publish-baseline`) | {' | '.join(fmt(totals['publish-baseline']))} |",
              f"| Seguro (`publish-secure`, enforce) | {' | '.join(fmt(totals['publish-secure']))} |"]
    return lines, totals


def client_times(records):
    audits = [a for a in records.get(("H0", "seguro-enforce", "audit"), []) if a.get("accepted")][-5:]
    lines = ["| Control en el cliente | Promedio (ms) | Desviación (ms) | Corridas |", "|---|---|---|---|"]
    for key, name in (("tuf", "TUF (refresh y descarga verificada de 4 archivos)"), ("cosign", "cosign verify-blob"),
                      ("slsa", "slsa-verifier verify-artifact")):
        values = [a["controls"][key]["ms"] for a in audits]
        sd = statistics.stdev(values) if len(values) > 1 else 0
        lines.append(f"| {name} | {statistics.mean(values):.0f} | {sd:.0f} | {len(values)} |")
    totals = [sum(a["controls"][k]["ms"] for k in ("tuf", "cosign", "slsa")) for a in audits]
    sd = statistics.stdev(totals) if len(totals) > 1 else 0
    lines.append(f"| **Total** | **{statistics.mean(totals):.0f}** | {sd:.0f} | {len(totals)} |")
    return lines


def main():
    records = load_json()
    matrix_lines, mismatches = matrix(records)
    times_lines, _ = pipeline_times()
    out = [
        "# Resultados de la prueba de concepto",
        "",
        "Generado por `scripts/make_results_table.py` a partir de `results/*.json` y `results/pipeline_times.csv`. "
        "La evidencia de cada celda está en `docs/evidence/<escenario>/`.",
        "",
        "## Matriz observada",
        "",
        "✅ = el control deja pasar · ❌ = el control bloquea · — = no aplica (el ataque no pasa por ese punto)",
        "",
        *matrix_lines,
        "",
        "\\* Valores de la configuración **seguro-report**: el artefacto se firmó igual, lo que demuestra que la "
        "firma por sí sola no habría detenido el ataque.",
        "",
        "## Diferencias con la matriz esperada",
        "",
        *(["Ninguna: la matriz observada coincide con la esperada en todas las filas."] if not mismatches else
          [f"- **{s}**: esperado {e}, observado {o}" for s, e, o in mismatches]),
        "",
        "## Tiempo que agrega cada control a la publicación (H0, `v1.1.2`)",
        "",
        "Duración de los pasos y *jobs* en GitHub Actions (`scripts/pipeline_times.py`), sin la espera de la "
        "aprobación manual. GitHub informa los tiempos con resolución de 1 s. La procedencia SLSA y la firma "
        "cosign corren en paralelo.",
        "",
        *times_lines,
        "",
        "## Tiempo de verificación en el cliente (H0, modo seguro)",
        "",
        "Auditorías de H0 con el *mirror* local (`time.perf_counter()` en `launcher/updater.py`).",
        "",
        *client_times(records),
        "",
    ]
    (RESULTS / "RESULTADOS.md").write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("\n".join(out))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

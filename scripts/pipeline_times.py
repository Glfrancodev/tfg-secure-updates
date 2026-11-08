"""Duración de cada job y paso de un run de GitHub Actions → results/pipeline_times.csv.

Usa `gh run view <id> --attempt N --json jobs`. Mide la duración de los jobs (del inicio de su primer paso
al fin del último), no la del run completo: la espera de la aprobación manual del environment `release`
queda fuera.

Con --record ESCENARIO CONFIG también guarda results/<ESCENARIO>-<CONFIG>-pipeline-<fecha>.json con el
resultado de cada gate. Un gate con continue-on-error figura como "success" en la API, así que el
resultado se toma de los reportes que sube el propio run (artifact "gate-reports").

Uso: python scripts/pipeline_times.py <run-id> [--attempt N | --all-attempts] [--record ESCENARIO CONFIG]
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "results" / "pipeline_times.csv"
FIELDS = ["run_id", "attempt", "workflow", "tag", "job", "step", "seconds"]


def gh(*args):
    result = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        sys.exit(f"gh {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def parse(timestamp):
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def run_data(run_id, attempt):
    return json.loads(gh("run", "view", str(run_id), "--attempt", str(attempt),
                         "--json", "jobs,workflowName,headBranch,headSha,conclusion,url,attempt"))


def time_rows(run_id, attempt, data):
    for job in data["jobs"]:
        steps = [s for s in job["steps"] if s.get("startedAt") and s.get("completedAt")
                 and not s["startedAt"].startswith("0001")]
        if job["conclusion"] == "skipped" or not steps:
            continue
        base = {"run_id": run_id, "attempt": attempt, "workflow": data["workflowName"],
                "tag": data["headBranch"], "job": job["name"]}
        start = min(parse(s["startedAt"]) for s in steps)
        end = max(parse(s["completedAt"]) for s in steps)
        yield {**base, "step": "(job)", "seconds": round((end - start).total_seconds(), 1)}
        for s in steps:
            seconds = (parse(s["completedAt"]) - parse(s["startedAt"])).total_seconds()
            yield {**base, "step": s["name"], "seconds": round(seconds, 1)}


def save_times(run_id, attempts):
    rows = []
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f)
                    if not (r["run_id"] == str(run_id) and int(r["attempt"]) in attempts)]
    for attempt in attempts:
        new = list(time_rows(run_id, attempt, run_data(run_id, attempt)))
        rows.extend({k: str(v) for k, v in r.items()} for r in new)
        job_total = sum(float(r["seconds"]) for r in new if r["step"] == "(job)")
        print(f"run {run_id} intento {attempt}: {len(new)} filas, suma de jobs {job_total:.0f} s")
    rows.sort(key=lambda r: (int(r["run_id"]), int(r["attempt"])))
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def gate_results(run_id):
    """Resultado de cada gate según los reportes del artifact gate-reports del run."""
    with tempfile.TemporaryDirectory() as tmp:
        gh("run", "download", str(run_id), "--name", "gate-reports", "--dir", tmp)
        read = lambda name: (Path(tmp) / name).read_text(encoding="utf-8", errors="replace") \
            if (Path(tmp) / name).exists() else None
        semgrep, clamav, yara, source = (read(n) for n in ("semgrep.txt", "clamav.txt", "yara.txt",
                                                           "source-match.txt"))
    infected = re.search(r"Infected files: (\d+)", clamav or "")
    return {
        "semgrep": "not_run" if semgrep is None else
                   "passed" if re.search(r"Findings: 0 \(0 blocking\)", semgrep) else "failed",
        "clamav": "not_run" if not infected else "passed" if infected.group(1) == "0" else "failed",
        "yara": "not_run" if yara is None else "failed" if yara.strip() else "passed",
        "source_match": "not_run" if source is None else
                        "failed" if "NO corresponde" in source else "passed",
    }


def record(run_id, attempt, scenario, config):
    data = run_data(run_id, attempt)
    gates = gate_results(run_id) if any(j["name"] == "gates" for j in data["jobs"]) else {}
    jobs = {j["name"]: j["conclusion"] for j in data["jobs"]}
    out = {
        "scenario": scenario, "config": config, "kind": "pipeline",
        "date": datetime.now().isoformat(timespec="seconds"),
        "run_id": int(run_id), "attempt": attempt, "tag": data["headBranch"], "commit": data["headSha"],
        "url": data["url"], "conclusion": data["conclusion"], "gates": gates,
        "published": jobs.get("release") == "success", "jobs": jobs,
    }
    path = ROOT / "results" / f"{scenario}-{config}-pipeline-{datetime.now():%Y%m%dT%H%M%S}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"gates: {gates} · publicado: {out['published']} → {path.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_id")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--attempt", type=int)
    group.add_argument("--all-attempts", action="store_true")
    parser.add_argument("--record", nargs=2, metavar=("ESCENARIO", "CONFIG"))
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    latest = json.loads(gh("run", "view", args.run_id, "--json", "attempt"))["attempt"]
    attempts = list(range(1, latest + 1)) if args.all_attempts else [args.attempt or latest]
    save_times(args.run_id, attempts)
    if args.record:
        record(args.run_id, attempts[-1], *args.record)


if __name__ == "__main__":
    main()

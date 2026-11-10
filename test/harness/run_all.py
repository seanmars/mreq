"""python run_all.py --trials 1 2 --problems justify lfu --variants old new --workers 4

Runs run_one.py then grade.py then judge.py for each (problem, variant, trial), in parallel.
Skips a trial whose results/<run>.json already exists.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = ROOT / "harness"


def job(problem, variant, trial):
    name = f"{problem}-{variant}-{trial}"
    if (ROOT / "results" / f"{name}.json").exists():
        return f"{name} skipped"
    for script, args in (("run_one.py", [problem, variant, str(trial)]), ("grade.py", [name]), ("judge.py", [name])):
        p = subprocess.run([sys.executable, str(H / script), *args], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if p.returncode != 0:
            return f"{name} {script} failed: {p.stderr[-500:]}"
    return f"{name} ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", nargs="+", type=int, required=True)
    ap.add_argument("--problems", nargs="+", default=["checkout", "sla", "booking", "tagval"])
    ap.add_argument("--variants", nargs="+", default=["old", "new"])
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    jobs = [(p, v, t) for t in a.trials for p in a.problems for v in a.variants]
    with ThreadPoolExecutor(a.workers) as ex:
        for line in ex.map(lambda j: job(*j), jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()

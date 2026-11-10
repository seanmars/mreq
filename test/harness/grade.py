"""Grade one run: python grade.py <run_name>  -> results/<run>.json"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "harness" / "cases.py"
MODULES = {"justify": "text_justify", "lfu": "lfu_cache", "regex": "regex_match", "tagval": "tag_validator",
           "checkout": "checkout", "sla": "sla", "booking": "booking"}


def run(args, cwd, timeout):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return None, "", "timeout"


def find_module(run_dir: Path, module: str):
    hits = [p for p in run_dir.rglob(f"{module}.py") if ".claude" not in p.parts and "tests" not in p.parts]
    return sorted(hits, key=lambda p: len(p.parts))[0] if hits else None


def doc_info(run_dir: Path):
    docs = sorted((run_dir / ".mreq").glob("*.md")) if (run_dir / ".mreq").exists() else []
    if not docs:
        return {"exists": False}
    text = docs[-1].read_text(encoding="utf-8")
    tasks = re.findall(r"^\s*- \[([ xX])\] ", text.split("## Tasks", 1)[-1].split("\n## ", 1)[0], re.M)
    terms = text.split("## Terms", 1)[1].split("\n## ", 1)[0] if "## Terms" in text else ""
    return {"exists": True, "path": str(docs[-1].relative_to(run_dir)), "chars": len(text),
            "status": (re.search(r'^status:\s*"?(\w+)"?', text, re.M) or [None, "?"])[1],
            "tasks_done": sum(1 for t in tasks if t != " "), "tasks_total": len(tasks),
            "terms": len(re.findall(r"^- \*\*", terms, re.M)), "bn": len(set(re.findall(r"\bB(\d+):", text)))}


def main():
    name = sys.argv[1]
    problem = name.split("-")[0]
    run_dir = ROOT / "runs" / name
    module = MODULES[problem]
    res = {"run": name, "doc": doc_info(run_dir)}
    path = find_module(run_dir, module)
    res["module_path"] = str(path.relative_to(run_dir)) if path else None
    if path:
        src = path.read_text(encoding="utf-8")
        res["loc"] = sum(1 for line in src.splitlines() if line.strip() and not line.strip().startswith("#"))
        res["uses_re"] = bool(re.search(r"^\s*(import re\b|from re import)", src, re.M))
        code, out, err = run(["python", str(CASES), problem, str(path.parent), "correct"], ROOT, 600)
        try:
            res["hidden"] = json.loads(out.strip().splitlines()[-1])
        except Exception:
            res["hidden"] = {"error": (err or out)[-500:]}
        code, out, _ = run(["python", str(CASES), problem, str(path.parent), "nperf"], ROOT, 60)
        perf = []
        for i in range(json.loads(out)["n"]):
            code, out, err = run(["python", str(CASES), problem, str(path.parent), "perf", str(i)], ROOT, 60)
            try:
                perf.append(json.loads(out.strip().splitlines()[-1]))
            except Exception:
                perf.append({"ok": False, "error": (err or "no output")[-200:]})
        res["perf"] = perf
    code, out, err = run(["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"], run_dir, 600)
    summary = (out.strip().splitlines() or [""])[-1]
    res["own_tests"] = {"exit": code, "summary": summary,
                        "passed": int((re.search(r"(\d+) passed", summary) or [0, 0])[1]),
                        "failed": int((re.search(r"(\d+) failed", summary) or [0, 0])[1])}
    (ROOT / "results").mkdir(exist_ok=True)
    old = ROOT / "results" / f"{name}.json"
    if old.exists():  # a regrade keeps the judge's verdict
        prev = json.loads(old.read_text(encoding="utf-8"))
        if "judge" in prev:
            res["judge"] = prev["judge"]
    (ROOT / "results" / f"{name}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()

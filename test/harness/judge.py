"""Read-only LLM judge: python judge.py <run_name>  -> adds "judge" to results/<run>.json

The judge gets only Read/Glob/Grep. It compares the code with the original request and with the
task document, and lists concrete bugs. It never sees hidden-test results.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = shutil.which("claude")
JUDGE_MODEL = "sonnet"

PROMPT = """You review the result of a coding task in this directory. Do not change any file.

The original request from the user:
<request>
{request}
</request>

The task document the agent wrote and followed is under .mreq/ (one .md file). The solution is `{module}`. The agent's tests are in this directory (find them).
Ignore the .claude/ directory.

Judge only the final code and tests. Read the request, the task document, the solution and the tests in full.
1. spec_conformance (1-5): does the code do every behavior the request and the task document ask for? Does it break any of them?
2. code_quality (1-5): clear, simple, idiomatic Python, right complexity.
3. test_quality (1-5): do the tests cover the rules and the edge cases of the request?
4. bugs: concrete inputs where the code gives a wrong result, each one checked by reading the code. Empty when none.
5. doc_drift: places where the code does something different from the task document. Empty when none.

Reply with only one JSON object, no prose:
{{"spec_conformance": n, "code_quality": n, "test_quality": n, "bugs": ["..."], "doc_drift": ["..."], "summary": "one sentence"}}
"""
MODULES = {"justify": "text_justify.py", "lfu": "lfu_cache.py", "regex": "regex_match.py", "tagval": "tag_validator.py",
           "checkout": "checkout.py", "sla": "sla.py", "booking": "booking.py"}


def main():
    name = sys.argv[1]
    problem = name.split("-")[0]
    run_dir = ROOT / "runs" / name
    res_path = ROOT / "results" / f"{name}.json"
    res = json.loads(res_path.read_text(encoding="utf-8"))
    request = (ROOT / "problems" / problem / "request.txt").read_text(encoding="utf-8").strip()
    prompt = PROMPT.format(request=request, module=res.get("module_path") or MODULES[problem])
    cmd = [CLAUDE, "-p", prompt, "--output-format", "json", "--model", JUDGE_MODEL, "--setting-sources", "project",
           "--tools", "Read", "Glob", "Grep", "--allowedTools", "Read", "Glob", "Grep"]
    p = subprocess.run(cmd, cwd=run_dir, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=30 * 60)
    try:
        data = json.loads(p.stdout)
        text = data.get("result", "")
        m = re.search(r"\{.*\}", text, re.S)
        judge = json.loads(m.group(0))
        judge["_cost"] = data.get("total_cost_usd")
    except Exception as e:
        judge = {"error": repr(e)[:200], "raw": (p.stdout + p.stderr)[-800:]}
    res["judge"] = judge
    res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(judge, ensure_ascii=False)[:500])


if __name__ == "__main__":
    main()

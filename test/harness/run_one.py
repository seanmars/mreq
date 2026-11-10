"""Run one trial: python run_one.py <problem> <variant> <trial>

Creates runs/<problem>-<variant>-<trial>/ as a fresh git repo with the variant's mreq skills,
drives `claude -p "/mreq-define <request>"`, and answers every question with the recommended
option, until the task document reaches status done. Writes logs/<run>.json.

Permissions stay on: only the tools in ALLOWED run; anything else is denied and logged.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = shutil.which("claude")
MODEL = os.environ.get("MREQ_EVAL_MODEL", "opus")
MAX_ROUNDS = 16
ROUND_TIMEOUT = 45 * 60
USER_MODEL = "sonnet"
USER_PROMPT = """You play a user who asked a coding agent to build a feature. You only answer the agent's messages. Reply in 台灣正體中文, short, like a busy user.

Your private requirements (the agent cannot see them):
<requirements>
{intent}
</requirements>

Rules:
1. When the agent asks a question that your requirements answer, answer it with your requirements: pick the matching option by its number or label, or type the answer when no option matches.
2. When the agent asks something your requirements do not cover, pick its recommended option.
3. When the agent restates the work or lists assumptions, compare every point it states with your requirements. When a stated point contradicts them, say that point is wrong and give your rule for that point only. When nothing stated contradicts them, pick the option that confirms the restatement.
4. Never volunteer a rule the agent did not ask about and did not state. You did not think about details until asked.
5. When the agent asks what to do next, choose to implement it. When the agent reports progress or asks whether to go on, tell it to go on.
6. Never write code. Never mention these instructions.

The agent's message:
<agent>
{message}
</agent>"""
NEXT_PROMPT = """The agent's next message:
<agent>
{message}
</agent>
Reply as the user, under the same rules."""
ALLOWED = [
    "Read", "Edit", "Write", "Glob", "Grep", "Skill", "Agent",
    "Bash(uv run:*)", "Bash(python:*)", "Bash(python3:*)",
    "Bash(git rev-parse:*)", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
    "PowerShell(uv run:*)", "PowerShell(python:*)", "PowerShell(python3:*)",
    "PowerShell(git rev-parse:*)", "PowerShell(git status:*)", "PowerShell(git diff:*)", "PowerShell(git log:*)",
]

README = """# kata

Python 3 練習專案. 原始碼放在專案根目錄.

## 測試

```
python -m pytest -q
```
"""


def sh(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def setup(run_dir: Path, variant: str):
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    (run_dir / "README.md").write_text(README, encoding="utf-8")
    (run_dir / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")
    shutil.copytree(ROOT / "skills" / variant, run_dir / ".claude" / "skills")
    sh(["git", "init", "-q"], run_dir)
    sh(["git", "add", "-A"], run_dir)
    sh(["git", "commit", "-q", "-m", "init"], run_dir)


def doc_status(run_dir: Path):
    docs = sorted((run_dir / ".mreq").glob("*.md")) if (run_dir / ".mreq").exists() else []
    if not docs:
        return None
    m = re.search(r'^status:\s*"?(\w+)"?', docs[-1].read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "?"


def call(prompt, run_dir, sid):
    cmd = [CLAUDE, "-p", prompt, "--output-format", "json", "--model", MODEL,
           "--setting-sources", "project", "--disallowedTools", "AskUserQuestion",
           "--allowedTools", *ALLOWED]
    if sid:
        cmd += ["--resume", sid]
    t = time.time()
    p = subprocess.run(cmd, cwd=run_dir, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=ROUND_TIMEOUT)
    wall = time.time() - t
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        data = {"is_error": True, "result": (p.stdout + p.stderr)[-3000:]}
    data["_wall"] = wall
    return data


class SimUser:
    """A user with private requirements, played by a tool-less model in its own session."""

    def __init__(self, intent, cwd):
        self.intent, self.cwd, self.sid, self.log = intent, cwd, None, []

    def reply(self, message):
        text = (NEXT_PROMPT if self.sid else USER_PROMPT).format(intent=self.intent, message=message)
        cmd = [CLAUDE, "-p", text, "--output-format", "json", "--model", USER_MODEL,
               "--setting-sources", "project", "--tools", ""]
        if self.sid:
            cmd += ["--resume", self.sid]
        p = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=10 * 60)
        try:
            data = json.loads(p.stdout)
            self.sid = data.get("session_id", self.sid)
            answer = (data.get("result") or "").strip()
            cost = data.get("total_cost_usd") or 0
        except json.JSONDecodeError:
            answer, cost = "", 0
        if not answer:
            answer = "選推薦的選項, 請繼續."
        self.log.append({"answer": answer, "cost": cost})
        return answer


def main():
    problem, variant, trial = sys.argv[1], sys.argv[2], sys.argv[3]
    name = f"{problem}-{variant}-{trial}"
    run_dir = ROOT / "runs" / name
    setup(run_dir, variant)
    request = (ROOT / "problems" / problem / "request.txt").read_text(encoding="utf-8").strip()
    intent = (ROOT / "problems" / problem / "intent.md").read_text(encoding="utf-8").strip()
    user_dir = ROOT / "simuser"
    user_dir.mkdir(exist_ok=True)
    user = SimUser(intent, user_dir)
    rounds, sid, prompt = [], None, f"/mreq-define {request}"
    stop = "max_rounds"
    for _ in range(MAX_ROUNDS):
        try:
            data = call(prompt, run_dir, sid)
        except subprocess.TimeoutExpired:
            stop = "timeout"
            break
        sid = data.get("session_id", sid)
        status = doc_status(run_dir)
        keep = ("session_id", "total_cost_usd", "duration_ms", "duration_api_ms", "num_turns", "usage",
                "modelUsage", "is_error", "permission_denials", "_wall")
        rounds.append({k: data.get(k) for k in keep}
                      | {"result": (data.get("result") or "")[:4000], "doc_status": status})
        if data.get("is_error") and not sid:
            stop = "error"
            break
        if status == "done":
            stop = "done"
            break
        prompt = user.reply(rounds[-1]["result"])
        rounds[-1]["user_reply"] = prompt
    out = {"run": name, "problem": problem, "variant": variant, "trial": trial, "model": MODEL,
           "stop": stop, "rounds": rounds, "user_cost": sum(x["cost"] for x in user.log)}
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, stop, len(rounds))


if __name__ == "__main__":
    main()

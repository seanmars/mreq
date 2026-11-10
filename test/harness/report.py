"""python report.py  -> report.md (per-run table, per-variant summary, per-problem comparison)"""
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tokens(log):
    t = defaultdict(int)
    cost = wall = api = turns = 0.0
    denials = 0
    for r in log["rounds"]:
        cost += r.get("total_cost_usd") or 0
        wall += r.get("_wall") or 0
        api += (r.get("duration_api_ms") or 0) / 1000
        turns += r.get("num_turns") or 0
        denials += len(r.get("permission_denials") or [])
        for m in (r.get("modelUsage") or {}).values():
            for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens"):
                t[k] += m.get(k, 0)
    return {"cost": cost, "wall_min": wall / 60, "api_min": api / 60, "turns": turns, "rounds": len(log["rounds"]),
            "in": t["inputTokens"], "out": t["outputTokens"], "cache_r": t["cacheReadInputTokens"],
            "cache_w": t["cacheCreationInputTokens"], "denials": denials}


def row(name):
    log = json.loads((ROOT / "logs" / f"{name}.json").read_text(encoding="utf-8"))
    res = json.loads((ROOT / "results" / f"{name}.json").read_text(encoding="utf-8"))
    h = res.get("hidden") or {}
    edge, rnd = h.get("edge", [0, 0]), h.get("random", [0, 0])
    total = edge[1] + rnd[1]
    perf = res.get("perf") or []
    j = res.get("judge") or {}
    return {"run": name, "problem": log["problem"], "variant": log["variant"], "stop": log["stop"],
            "hidden_pct": 100 * (edge[0] + rnd[0]) / total if total else 0.0,
            "edge": f"{edge[0]}/{edge[1]}", "random": f"{rnd[0]}/{rnd[1]}",
            "perf_ok": sum(1 for p in perf if p.get("ok")), "perf_n": len(perf),
            "all_pass": total > 0 and edge[0] + rnd[0] == total and all(p.get("ok") for p in perf),
            "own_pass": (res.get("own_tests") or {}).get("passed", 0),
            "own_fail": (res.get("own_tests") or {}).get("failed", 0),
            "loc": res.get("loc"), "uses_re": res.get("uses_re"),
            "doc_status": (res.get("doc") or {}).get("status"), "terms": (res.get("doc") or {}).get("terms"),
            "bn": (res.get("doc") or {}).get("bn"),
            "spec": j.get("spec_conformance"), "quality": j.get("code_quality"), "tests_q": j.get("test_quality"),
            "bugs": len(j.get("bugs") or []), "drift": len(j.get("doc_drift") or []),
            "fails": h.get("fails", []), "judge_bugs": j.get("bugs") or [], "rules": h.get("rules") or {},
            "rules_ok": sum(1 for v in (h.get("rules") or {}).values() if v[0] == v[1]),
            "rules_n": len(h.get("rules") or {}), "user_cost": log.get("user_cost", 0), **tokens(log)}


VARIANTS = ["old", "new", "slim"]
NAMES = {"old": "舊版", "new": "新版", "slim": "精簡版"}


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return st.mean(xs) if xs else float("nan")


def sd(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return st.stdev(xs) if len(xs) > 1 else 0.0


METRICS = [("全部通過率 (hidden+perf)", lambda rs: 100 * mean([1 if r["all_pass"] else 0 for r in rs]), "{:.0f}%"),
           ("意圖規則全對 (平均每次)", lambda rs: 100 * mean([r["rules_ok"] / r["rules_n"] for r in rs if r["rules_n"]]), "{:.1f}%"),
           ("Hidden 正確率", lambda rs: mean([r["hidden_pct"] for r in rs]), "{:.2f}%"),
           ("Perf 通過", lambda rs: f'{sum(r["perf_ok"] for r in rs)}/{sum(r["perf_n"] for r in rs)}', "{}"),
           ("Judge: 符合規格 (1-5)", lambda rs: mean([r["spec"] for r in rs]), "{:.2f}"),
           ("Judge: 程式品質 (1-5)", lambda rs: mean([r["quality"] for r in rs]), "{:.2f}"),
           ("Judge: 測試品質 (1-5)", lambda rs: mean([r["tests_q"] for r in rs]), "{:.2f}"),
           ("Judge: bug 數 (合計)", lambda rs: sum(r["bugs"] for r in rs), "{}"),
           ("Judge: 與文件不一致 (合計)", lambda rs: sum(r["drift"] for r in rs), "{}"),
           ("自帶測試數 (平均)", lambda rs: mean([r["own_pass"] + r["own_fail"] for r in rs]), "{:.1f}"),
           ("自帶測試失敗 (合計)", lambda rs: sum(r["own_fail"] for r in rs), "{}"),
           ("成本 USD (平均)", lambda rs: mean([r["cost"] for r in rs]), "${:.2f}"),
           ("成本 USD (標準差)", lambda rs: sd([r["cost"] for r in rs]), "${:.2f}"),
           ("Output tokens (平均)", lambda rs: mean([r["out"] for r in rs]), "{:,.0f}"),
           ("Input tokens 未快取 (平均)", lambda rs: mean([r["in"] for r in rs]), "{:,.0f}"),
           ("Cache read tokens (平均)", lambda rs: mean([r["cache_r"] for r in rs]), "{:,.0f}"),
           ("Cache write tokens (平均)", lambda rs: mean([r["cache_w"] for r in rs]), "{:,.0f}"),
           ("Wall time 分鐘 (平均)", lambda rs: mean([r["wall_min"] for r in rs]), "{:.1f}"),
           ("Agent turns (平均)", lambda rs: mean([r["turns"] for r in rs]), "{:.1f}"),
           ("使用者回覆輪數 (平均)", lambda rs: mean([r["rounds"] for r in rs]), "{:.1f}"),
           ("程式碼行數 (平均)", lambda rs: mean([r["loc"] for r in rs]), "{:.0f}"),
           ("完成 (status done)", lambda rs: f'{sum(1 for r in rs if r["stop"] == "done")}/{len(rs)}', "{}")]


def fmt(f, v):
    try:
        return f.format(v)
    except (ValueError, TypeError):
        return str(v)


def main():
    names = sorted(p.stem for p in (ROOT / "results").glob("*.json") if (ROOT / "logs" / f"{p.stem}.json").exists())
    rows = [row(n) for n in names]
    by_v = defaultdict(list)
    for r in rows:
        by_v[r["variant"]].append(r)
    vs = [v for v in VARIANTS if by_v[v]]
    head = " | ".join(NAMES[v] for v in vs)
    sep = "|".join("---" for _ in vs)
    out = ["# mreq " + " vs ".join(NAMES[v] for v in vs) + " 比較報告", ""]
    out += ["## 總表 (所有題目)", "", f"| 指標 | {head} |", f"|---|{sep}|"]
    for label, fn, f in METRICS:
        out.append(f"| {label} | " + " | ".join(fmt(f, fn(by_v[v])) for v in vs) + " |")
    out += ["", "樣本數: " + ", ".join(f"{NAMES[v]} {len(by_v[v])} 次" for v in vs) +
            ". 成本與 token 只算被測的 agent; 模擬使用者另計 (" +
            ", ".join(f"{NAMES[v]} ${sum(r['user_cost'] for r in by_v[v]):.2f}" for v in vs) + ").", ""]
    out += ["## 各題比較", "", "| 題目 | 版本 | n | 全部通過 | Hidden 正確率 | Perf | Judge 規格/品質/測試 | 成本 USD | Output tokens | 時間 (分) |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    probs = sorted({r["problem"] for r in rows})
    for p in probs:
        for v in vs:
            rs = [r for r in rows if r["problem"] == p and r["variant"] == v]
            if not rs:
                continue
            out.append(f"| {p} | {v} | {len(rs)} | {sum(r['all_pass'] for r in rs)}/{len(rs)} | "
                       f"{mean([r['hidden_pct'] for r in rs]):.2f}% | {sum(r['perf_ok'] for r in rs)}/{sum(r['perf_n'] for r in rs)} | "
                       f"{mean([r['spec'] for r in rs]):.1f}/{mean([r['quality'] for r in rs]):.1f}/{mean([r['tests_q'] for r in rs]):.1f} | "
                       f"${mean([r['cost'] for r in rs]):.2f} | {mean([r['out'] for r in rs]):,.0f} | {mean([r['wall_min'] for r in rs]):.1f} |")
    out += ["", "## 各意圖規則: 全對的次數 (只列有差異的規則)", ""]
    for p in probs:
        labels = []
        for r in rows:
            if r["problem"] == p:
                labels += [k for k in r["rules"] if k not in labels and k != "edge"]
        lines = []
        for lab in labels:
            cells = []
            for v in vs:
                rs = [r for r in rows if r["problem"] == p and r["variant"] == v]
                ok = sum(1 for r in rs if lab in r["rules"] and r["rules"][lab][0] == r["rules"][lab][1])
                cells.append(f"{ok}/{len(rs)}")
            if len(set(cells)) > 1:
                lines.append(f"| {lab} | " + " | ".join(cells) + " |")
        out += [f"### {p}", ""]
        out += ([f"| 規則 | {head} |", f"|---|{sep}|"] + lines) if lines else [f"所有 {len(labels)} 條規則在各版本的結果相同."]
        out.append("")
    out += ["", "## 每次執行明細", "",
            "| run | stop | edge | random | perf | 自帶測試 | LOC | Terms | Bn | Judge | 成本 | out tok | 分鐘 | turns | 輪數 | 拒絕 |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['run']} | {r['stop']} | {r['edge']} | {r['random']} | {r['perf_ok']}/{r['perf_n']} | "
                   f"{r['own_pass']}P/{r['own_fail']}F | {r['loc']} | {r['terms']} | {r['bn']} | "
                   f"{r['spec']}/{r['quality']}/{r['tests_q']} | ${r['cost']:.2f} | {r['out']:,} | {r['wall_min']:.1f} | "
                   f"{r['turns']:.0f} | {r['rounds']} | {r['denials']} |")
    out += ["", "## 失敗案例與 judge 找到的 bug", ""]
    for r in rows:
        if r["fails"] or r["judge_bugs"] or r["perf_ok"] < r["perf_n"]:
            out.append(f"### {r['run']}")
            for f in r["fails"][:3]:
                out.append(f"- hidden: `{json.dumps(f, ensure_ascii=False)[:300]}`")
            if r["perf_ok"] < r["perf_n"]:
                out.append(f"- perf: {r['perf_ok']}/{r['perf_n']} 通過")
            for b in r["judge_bugs"][:3]:
                out.append(f"- judge: {b[:300]}")
            out.append("")
    (ROOT / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (ROOT / "report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(out[:40]))


if __name__ == "__main__":
    main()

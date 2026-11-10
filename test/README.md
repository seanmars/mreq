# mreq skill 比較測試

用同一組題目, 比較兩個或多個版本的 mreq skill. 評估只看 `/mreq-define` → `mreq-apply` 之後的最終產出: 程式碼是否符合使用者意圖, 是否有 bug, 使用多少 token, 花多少時間. 中間的任務文件格式不列入評分.

題目的內容與每題的陷阱, 見 [PROBLEMS.md](PROBLEMS.md).

## 測試流程

每個 run 都是一次獨立的 `define → apply`:

```
建立空的 git repo (放入受測版本的 skill)
  → claude -p "/mreq-define <需求>"
  → agent 提問 ⇄ 模擬使用者依意圖卡回答 (多輪, --resume 接續同一個 session)
  → agent 寫文件, 執行 mreq-apply, 把文件設成 done
  → hidden test 評分 → agent 自帶測試 → judge 審查
```

1. `run_one.py` 建立 `runs/<題目>-<版本>-<次數>/`: 寫入 `README.md` (說明測試指令 `python -m pytest -q`) 和 `.gitignore`, 把 `skills/<版本>/` 複製到 `.claude/skills/`, 然後 `git init` 並 commit.
2. 第一輪送出 `/mreq-define <request.txt 的內容>`.
3. 每一輪結束後檢查 `.mreq/*.md` 的 `status`. 是 `done` 就停止.
4. 不是 `done` 時, 把 agent 這一輪的最後訊息交給模擬使用者, 再把模擬使用者的回答用 `--resume` 送回 agent.
5. 最多 16 輪. 單輪超過 45 分鐘就停止.
6. `grade.py` 評分, `judge.py` 審查, 結果寫入 `results/<run>.json`.

### 被測 agent 的設定

```
claude -p <prompt> --output-format json --model opus
       --setting-sources project
       --disallowedTools AskUserQuestion
       --allowedTools Read Edit Write Glob Grep Skill Agent
                      "Bash(uv run:*)" "Bash(python:*)" "Bash(python3:*)"
                      "Bash(git rev-parse:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)"
                      (同樣的指令也開放給 PowerShell)
```

- `--setting-sources project`: 不載入使用者層級的 settings 和 plugin. 兩版看到的環境相同. 使用者的全域 `CLAUDE.md` 仍會載入, 兩版相同.
- `--disallowedTools AskUserQuestion`: headless 模式無法回答選項對話框. skill 會改用純文字編號清單提問, 模擬使用者用文字回答.
- 不使用 `bypassPermissions`. 白名單以外的工具一律被拒絕, 每次拒絕都記錄在 log 的 `permission_denials`.

## 模擬使用者

模擬使用者由 `sonnet` 扮演, 沒有任何工具 (`--tools ""`), 用自己的 session 保留對話脈絡. 它手上有該題的意圖卡 (`problems/<題目>/intent.md`), agent 看不到這張卡.

它的回答規則 (完整 prompt 見 `harness/run_one.py` 的 `USER_PROMPT`):

1. agent 問到意圖卡涵蓋的問題: 依意圖卡回答. 有對應的選項就選, 沒有就打字回答.
2. agent 問到意圖卡沒涵蓋的問題: 選推薦選項.
3. agent restate 或列出 Assumptions 時: 逐點和意圖卡比對. 有矛盾的點, 只糾正那一點. 沒有矛盾, 就選確認的選項.
4. 不主動說出 agent 沒問, 也沒寫出來的規則.
5. 問下一步時選實作. 回報進度時要它繼續.

這個設計讓 "define 有沒有問對問題, 有沒有把假設攤開" 直接影響最終程式碼. agent 沒問到, 也沒寫在 restate 裡的規則, 使用者就不會糾正, 最後會變成 hidden test 的失敗.

## 評分

### Hidden test (`harness/cases.py`)

agent 看不到 hidden test. 每題有一份依意圖卡寫的參考實作, 評分分成三部分:

| 部分 | 內容 |
|---|---|
| 規則案例 (edge) | 每個案例標示它檢查哪一條意圖規則 (例如 `round half up once`). 報表依規則列出每個版本全對的次數. |
| 隨機差分 (random) | 固定 seed (`20261109`) 產生 3000 組輸入, 比對受測程式與參考實作的輸出. 例外以型別名稱比對, 例如兩邊都丟 `ValueError` 就算相同. |
| 效能 (perf) | 只有部分題目有. 每個案例在獨立的子行程執行, 有時間上限. |

`grade.py` 在 run 目錄中找題目指定的模組檔名 (排除 `.claude/` 和 `tests/`), 把它的目錄加入 `sys.path` 後 import. 它也會記錄:

- agent 自帶測試的結果: 執行 `python -m pytest -q`.
- 程式碼行數: 不含空行和註解.
- 文件資訊: 狀態, task 進度, `## Terms` 項目數, `Bn` 數量.

### Judge (`harness/judge.py`)

judge 由 `sonnet` 扮演, 只有 Read, Glob 和 Grep 三個工具. 它會讀原始需求, 任務文件, 程式碼和測試, 然後回傳 JSON:

- `spec_conformance`, `code_quality`, `test_quality`: 1 到 5 分.
- `bugs`: 具體的錯誤輸入.
- `doc_drift`: 程式碼和文件不一致的地方.

judge 看不到 hidden test 的結果. 重新評分 (`grade.py`) 時會保留已有的 judge 結果.

### 指標

| 指標 | 定義 |
|---|---|
| 全部通過率 | edge, random 和 perf 全部通過的 run 所占的比例 |
| 意圖規則全對 | 每個 run 中, edge 案例全對的規則占全部規則的比例, 再取平均 |
| 成本 | 每一輪 `total_cost_usd` 的總和. 只算被測 agent, 模擬使用者另計 |
| Token | 每一輪 `modelUsage` 的總和, 包含 subagent. 分成 output, 未快取 input, cache read 和 cache write |
| 時間 | 每一輪 `claude -p` 的 wall time 總和 |
| Agent turns | 每一輪 `num_turns` 的總和 |
| 回覆輪數 | `claude -p` 的呼叫次數 |

## 目錄結構

```
test/
├── README.md        # 本文件
├── PROBLEMS.md      # 題目, 意圖卡, hidden test 規則
├── harness/
│   ├── run_one.py   # 跑一個 run: 建 repo, 驅動 agent 與模擬使用者
│   ├── run_all.py   # 平行跑多個 run, 依序呼叫 run_one, grade, judge
│   ├── cases.py     # hidden test 與參考實作
│   ├── grade.py     # 評分
│   ├── judge.py     # LLM judge
│   ├── report.py    # 產生 report.md 與 report.json
│   └── selftest/    # 驗證 grader 的正確解 (good) 與 O(n) 解 (naive)
├── problems/<題目>/
│   ├── request.txt  # 使用者的原始需求 (agent 看得到)
│   └── intent.md    # 意圖卡 (只有模擬使用者看得到)
└── (執行時產生, 已加入 .gitignore) skills/ runs/ logs/ results/ simuser/ report.md report.json
```

## 執行方式

需要 `claude` CLI (已登入), Python 3.10 以上, `pytest`, `jq` (只用於查看結果). 以下指令都在 `test/` 目錄下執行.

1. 匯出要比較的 skill 版本. 每個版本放在 `skills/<版本名稱>/`:

   ```sh
   mkdir -p skills/old skills/new
   git -C .. archive c7cb499 skills | tar -x -C skills/old --strip-components=1
   cp -r ../skills/. skills/new/          # 或 git archive 另一個 commit
   ```

2. 驗證 grader. 每一題的正確解都要全部通過:

   ```sh
   for p in checkout sla booking tagval; do python harness/cases.py $p harness/selftest/good correct; done
   ```

3. 先跑一題 pilot, 確認流程正常:

   ```sh
   python harness/run_all.py --trials 0 --problems checkout --variants old new --workers 2
   jq -r '.rounds[] | .result[0:500], "USER: " + (.user_reply // "-")' logs/checkout-new-0.json
   ```

   檢查模擬使用者是否只回答被問到的問題.

4. 跑完整測試, 然後產生報表:

   ```sh
   python harness/run_all.py --trials 0 1 2 --variants old new --workers 4
   python harness/report.py
   ```

`run_all.py` 會跳過 `results/` 中已經存在的 run. 要重跑某個 run 時, 先刪除它的 `results/<run>.json`. 預設題目是 `checkout sla booking tagval`. `report.py` 認得的版本名稱是 `old`, `new`, `slim`. 新增其他名稱時, 要修改 `report.py` 的 `VARIANTS` 和 `NAMES`.

成本參考 (Opus, 2026-11): 每個 run 約 $1.5 到 $4, 約 2 到 6 分鐘. 4 題 × 2 版 × 3 次約 $55, workers 4 時約 1 小時.

## 已知限制

- **天花板效應**: Opus 搭配舊版 mreq, 已經能把這幾題做到 100%. 正確率只能分辨 "變差", 很難分辨 "變好".
- **模擬使用者偶爾主動透露規則**: 例如在回答選項時順便補充 "同 sku 要先合併", 違反規則 4. 這會縮小兩版的差異.
- **樣本數**: 每題每版 3 次. 1 次失敗不足以判斷版本優劣. 成本差異要看配對比較 (同一題同一次的兩版互比).
- **Judge 的變異**: judge 分數的差距在 0.2 以內時, 視為雜訊.
- **單次 session**: define 和 apply 在同一個 session 執行. 測不到 "不同 agent 接手文件" 的情境.
- **範例污染**: 受測 skill 的範例不可以和題目同一個領域. 否則 agent 讀 skill 時就先看到答案.

## 新增題目

1. 建立 `problems/<題目>/request.txt`: 寫成使用者會說的話, 指定檔名和 API 名稱, 讓 hidden test 能 import. 規則刻意留白.
2. 建立 `problems/<題目>/intent.md`: 列出留白規則的答案, 一條一行.
3. 在 `cases.py` 加一個 `@problem("<題目>")` class: 包含 `module`, `attr`, `LABELED = True`, 依規則標記的 `EDGE`, `gen`, `call`, `ref`, `perf_cases`. 例外用 `catch()` 包起來, 以型別名稱比對.
4. 在 `grade.py` 和 `judge.py` 的 `MODULES` 加入模組名稱.
5. 在 `selftest/good/` 放一個呼叫參考實作的模組, 執行第 2 步驗證.
6. 印出每個 edge 案例的期望值, 逐一和意圖卡人工核對.

## 2026-11 的結果

比較三個版本. 舊版是 `c7cb499`. 新版是 `193e1fb`, 加入 `SPEC.md` 的完整規則, 存在 branch `feat/spec-rules`. 精簡版存在 stash. 每版各跑 12 次 (4 題 × 3 次).

| 指標 | 舊版 | 新版 | 精簡版 |
|---|---|---|---|
| hidden test 全部通過 | 12/12 | 11/12 | 12/12 |
| Judge 規格符合 (1-5) | 4.92 | 4.92 | 4.92 |
| Judge 回報的文件不一致 | 1 | 5 | 0 |
| 成本 (平均) | $1.95 | $2.77 | $2.24 |
| Output tokens (平均) | 28,885 | 42,329 | 33,862 |
| 時間 (平均) | 3.0 分 | 3.8 分 | 3.2 分 |

結論: 新規則沒有提高正確性, 成本增加 15% 到 42%. 所以維持舊版.

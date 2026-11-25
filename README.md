# mreq

## Skill

| Skill | 作用 | 誰能呼叫 |
|---|---|---|
| `mreq-define` | 判斷意圖 (feature / issue / refactor / task),訪談,確認後產生文件. 小需求可以不寫文件, 直接實作,  Request for Proposal(RFP) | 只有使用者 |
| `mreq-grill` | 用四象限壓力測試文件,把結論寫回文件 | 使用者, agent |
| `mreq-apply` | 逐項實作文件的 Tasks,更新 checkbox 和 Handoff | 使用者, agent |
| `mreq-close` | 核對程式碼與文件,通過後刪除文件 | 只有使用者 |
| `mreq-how` | 先確認問題的解讀,再產生解說程式碼的離線 HTML,附 Mermaid 圖表與圖例,放在 session root 的 `.mreq/how/`. 加 `--plain` 改寫給企劃, PM 等非程式人員: 用功能名詞, 不放程式碼位置 | 只有使用者 |
| `mreq-graph` | 先確認描述的解讀,再把描述畫成 Mermaid 圖表,產生附圖例的離線 HTML,放在 session root 的 `.mreq/graph/` | 只有使用者 |
| `mreq-pro` | 改寫 prompt, 要求頂尖專家的做法: 更深, 不是更大. 先回答關鍵難點, 原始資料, 方法與工具, 外部驗證, 再給出可複製的新 prompt. 沒有給 prompt 時, 改寫最近一次的需求; 對話裡有 `mreq-terms` 的結果時, 改寫它給的 prompt | 只有使用者 |
| `mreq-terms` | 使用者有想法, 但缺少專家的術語與知識時使用. 依照 prompt, 對話與檔案, 給出 5 到 12 個適合的術語 (意思, 專家知道的事, 已打開確認的連結), 看起來對但不適合的術語, 2 到 3 個相鄰領域, 使用者沒提到的事, 再用術語改寫 prompt. 沒有給 prompt 時, 使用最近一次的需求. 接著輸入 `/mreq-pro` (不給 prompt), 就會加深這個新 prompt | 只有使用者 |

「誰能呼叫」由各 agent 自己的設定控制. Claude Code, Grok 與 Antigravity 讀 SKILL.md 的 `disable-model-invocation`. Codex 讀各 skill 的 `agents/openai.yaml` (`allow_implicit_invocation: false`). 其他 agent 可能兩者都不讀, 模型可能自動觸發任何一個 skill. `mreq-close` 核對通過後會直接刪除文件.

典型流程: `/mreq-define` → (`mreq-grill`) → `mreq-apply` → commit (程式碼和 `.mreq/`) → `/mreq-close`.

小需求流程: `/mreq-define` → 確認重述時選「直接實作, 不寫文件」(小需求的推薦選項) → 在同一個 session 實作 → 對照重述回報. 這個流程不產生文件, 也不需要 `/mreq-close`. 實作前也可以選「先 grill, 不寫文件」: `mreq-define` 自己 grill 重述, 然後再重述一次. 需求是 Simple 而且沒有延後的決策時, `mreq-define` 才提供這個選項; 你也可以在文字欄直接要求不寫文件. 工作超出重述的範圍或中途停止時, `mreq-define` 會補寫文件, 之後用 `mreq-apply` 接續.

skill 之間能自動接續的地方, 不需要輸入指令. `mreq-define` 與 `mreq-grill` 確認重述的那一題同時選下一步, 寫完文件後不再多問一次: `mreq-define` 可接 `mreq-grill` 或 `mreq-apply`, `mreq-grill` 與 `mreq-apply` 可互相接續, `mreq-close` 發現未完成的 task, 失敗的測試或要修正的 finding 時, 可帶著它們接 `mreq-apply`. `mreq-grill` 確認時也可以選「寫回後繼續 grill」: 已確認的結論先寫回文件, 然後直接開始下一輪. 同一個對話的下一輪只 grill 有變更的項目, 仍未決的項目與你指定的焦點. 第一輪也可以指定焦點, 例: `/mreq-grill <path> 錯誤處理`: 四象限仍然全部掃描, 但焦點的部分問得更深, 並先回報. 「只有使用者」能呼叫的 skill 不會被自動接續, 這時 skill 會給出完整的指令讓你執行.

agent 有選項提問的 tool 時, 每個問題都用選項回答: Claude Code 的 `AskUserQuestion`, Grok 的 `ask_user_question`, Antigravity 的 `ask_question`, Codex 的 `request_user_input` (只在 Plan mode). 選項沒有你要的答案時, 在選項下方的文字欄輸入. 沒有這種 tool 時, skill 用編號清單提問.

`mreq-apply` 不會自己 commit. `mreq-close` 刪除前不檢查 git 狀態, 也不詢問. 沒有指定路徑, 而且只有一份 `done` 的文件時, `/mreq-close` 直接核對那一份. 要保留文件內容, 請先 commit, 再執行 `/mreq-close`.

`/mreq-close` 可以在任何 session 執行, 包括做修改的同一個 session. 它只依照現在讀到的文件與程式碼判斷, 不依照對話記憶.

## 安裝

每個 skill 都帶著自己需要的檔案, 所以可以只安裝部分 skill. 下面兩種方式選一種, 不要同時使用.

### Claude Code plugin

```sh
claude plugin marketplace add seanmars/mreq
claude plugin install mreq@mreq
```

plugin 一定會安裝全部 skill. skill 名稱前會加上 `mreq:`, 例如 `/mreq:mreq-define`. 沒有其他同名指令時, `/mreq-define` 也能用.

### 其他 agent

使用 [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI 安裝. `--skill '*'` 選擇全部 skill, `-a` 選擇 agent.

```sh
npx skills add seanmars/mreq --skill '*' -a codex
```

| Agent | `-a` | 安裝位置 (project) | 呼叫方式 |
|---|---|---|---|
| Codex | `codex` | `.agents/skills/` | `$mreq-define <request>`, 或 `/skills` 選擇 |
| Grok Build | `grok` | `.grok/skills/` | `/mreq-define <request>` |
| Antigravity | `antigravity` | `.agents/skills/` | `/mreq-define <request>` |

- 只安裝部分 skill 時, 自動接續只能接到已安裝的 skill. 例: `mreq-define` 接 `mreq-apply`, 兩個都要安裝.
- 請安裝在 project, 不要加 `-g`. Codex 與 Antigravity 的 sandbox 可能讀不到 home 目錄下的 skill.
- 已經用 plugin 安裝時, 不要再用 `-a claude-code` 安裝. Claude Code 會同時載入兩份.
- sandbox 封鎖 `uv` 時 (沒有網路, 或 uv cache 不可寫入), skill 會改用 `python`. 同一個對話只會失敗一次.

## 需求

`uv`, 或 Python 3.10 以上. script 只用標準函式庫.

安裝時需要 Node.js (`npx`). 使用 skill 時不需要. `mreq-how` 與 `mreq-graph` 有 Node.js 時會在 build 時檢查每張圖; 沒有時仍會產生頁面, 但不檢查.

## 目錄結構

```
.claude-plugin/
└── marketplace.json  # Claude Code plugin marketplace, plugin 為整個 repo
skills/           # 只限使用者呼叫的 skill 另有 agents/openai.yaml (Codex)
├── mreq-define/  # SKILL.md, EXPLORER.md, templates/, 複本: scripts/mreq.py, GRILL.md
├── mreq-grill/   # 複本: scripts/mreq.py, GRILL.md
├── mreq-apply/   # 複本: scripts/mreq.py
├── mreq-close/   # 複本: scripts/mreq.py
├── mreq-how/     # SKILL.md, EXPLORER.md, WRITING.md, skeleton.html, 複本: scripts/page.py, scripts/check.mjs, vendor/ (Pele), MERMAID.md
├── mreq-graph/   # SKILL.md, WRITING.md, skeleton.html, 複本同 mreq-how
├── mreq-pro/
└── mreq-terms/
shared/           # 複本的來源, 不是 skill: scripts/, vendor/, GRILL.md, MERMAID.md
tools/
└── sync.py       # 把 shared/ 的檔案複製到使用它的 skill
tests/            # python -m unittest discover -s tests
```

多個 skill 使用的檔案只在 `shared/` 修改. 修改後執行 `python tools/sync.py`. 不要直接修改 skill 裡的複本: 複本與 `shared/` 不同時, 測試會失敗.
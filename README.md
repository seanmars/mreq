# mreq

## Skill

| Skill | 作用 | 誰能呼叫 |
|---|---|---|
| `mreq-define` | 判斷意圖 (feature / issue / refactor / task),訪談,確認後產生文件. 小需求可以不寫文件, 直接實作 | 只有使用者 |
| `mreq-grill` | 用四象限壓力測試文件,把結論寫回文件 | 使用者, agent |
| `mreq-apply` | 逐項實作文件的 Tasks,更新 checkbox 和 Handoff | 使用者, agent |
| `mreq-close` | 核對程式碼與文件,通過後刪除文件 | 只有使用者 |
| `mreq-how` | 先確認問題的解讀,再產生解說程式碼的離線 HTML,附 Mermaid 圖表與圖例,放在 session root 的 `.mreq/how/`. 加 `--plain` 改寫給企劃, PM 等非程式人員: 用功能名詞, 不放程式碼位置 | 只有使用者 |
| `mreq-graph` | 先確認描述的解讀,再把描述畫成 Mermaid 圖表,產生附圖例的離線 HTML,放在 session root 的 `.mreq/graph/` | 只有使用者 |
| `mreq-shared` | 不執行任何任務. 放其他 skill 共用的 script, template, Pele, grill 方法, 與 Mermaid 規則 | 沒有人 |

「誰能呼叫」只適用 Claude Code. 其他 agent 不讀 `disable-model-invocation`, 模型可能自動觸發任何一個 skill. `mreq-close` 核對通過後會直接刪除文件.

典型流程: `/mreq-define` → (`mreq-grill`) → `mreq-apply` → commit (程式碼和 `.mreq/`) → `/mreq-close`.

小需求流程: `/mreq-define` → 確認重述時選「直接實作, 不寫文件」(小需求的推薦選項) → 在同一個 session 實作 → 對照重述回報. 這個流程不產生文件, 也不需要 `/mreq-close`. 實作前也可以選「先 grill, 不寫文件」: `mreq-define` 自己 grill 重述, 然後再重述一次. 需求是 Simple 而且沒有延後的決策時, `mreq-define` 才提供這個選項; 你也可以在文字欄直接要求不寫文件. 工作超出重述的範圍或中途停止時, `mreq-define` 會補寫文件, 之後用 `mreq-apply` 接續.

skill 之間能自動接續的地方, 不需要輸入指令. `mreq-define` 與 `mreq-grill` 確認重述的那一題同時選下一步, 寫完文件後不再多問一次: `mreq-define` 可接 `mreq-grill` 或 `mreq-apply`, `mreq-grill` 與 `mreq-apply` 可互相接續, `mreq-close` 發現未完成的 task, 失敗的測試或要修正的 finding 時, 可帶著它們接 `mreq-apply`. 「只有使用者」能呼叫的 skill 不會被自動接續, 這時 skill 會給出完整的指令讓你執行.

Claude Code 有 `AskUserQuestion` 時, 每個問題都用選項回答. 選項沒有你要的答案時, 在選項下方的文字欄輸入.

`mreq-apply` 不會自己 commit. `mreq-close` 刪除前不檢查 git 狀態, 也不詢問. 沒有指定路徑, 而且只有一份 `done` 的文件時, `/mreq-close` 直接核對那一份. 要保留文件內容, 請先 commit, 再執行 `/mreq-close`.

`/mreq-close` 可以在任何 session 執行, 包括做修改的同一個 session. 它只依照現在讀到的文件與程式碼判斷, 不依照對話記憶.

## 安裝

請一次安裝全部 skill. 其他 skill 都使用 `mreq-shared` 裡的檔案, 沒有 `mreq-shared` 就不能執行. 下面兩種方式選一種, 不要同時使用.

### Claude Code plugin

```sh
claude plugin marketplace add seanmars/mreq
claude plugin install mreq@mreq
```

plugin 一定會安裝全部 skill. skill 名稱前會加上 `mreq:`, 例如 `/mreq:mreq-define`. 沒有其他同名指令時, `/mreq-define` 也能用.

### 其他 agent

使用 [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI 安裝. `--skill '*'` 選擇全部 skill.

```sh
npx skills add seanmars/mreq --skill '*'
```

只安裝部分 skill 時, 一定要包含 `mreq-shared`.

## 需求

`uv`,或 Python 3.10 以上.script 只用標準函式庫.

安裝時需要 Node.js (`npx`). 使用 skill 時不需要. `mreq-how` 與 `mreq-graph` 有 Node.js 時會在 build 時檢查每張圖; 沒有時仍會產生頁面, 但不檢查.

## 目錄結構

```
.claude-plugin/
└── marketplace.json  # Claude Code plugin marketplace, plugin 為整個 repo
skills/
├── mreq-define/  # SKILL.md, EXPLORER.md
├── mreq-grill/
├── mreq-apply/
├── mreq-close/
├── mreq-how/     # SKILL.md, EXPLORER.md, WRITING.md, skeleton.html
├── mreq-graph/   # SKILL.md, WRITING.md, skeleton.html
└── mreq-shared/  # 共用: scripts/mreq.py, scripts/page.py, templates/, scripts/check.mjs, vendor/ (Pele), GRILL.md, MERMAID.md
tests/            # python -m unittest discover -s tests
```
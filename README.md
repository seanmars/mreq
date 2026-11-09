# mreq

## Skill

| Skill | 作用 | 誰能呼叫 |
|---|---|---|
| `mreq-define` | 判斷意圖 (feature / issue / refactor / task),訪談,確認後產生文件 | 只有使用者 |
| `mreq-grill` | 用四象限壓力測試文件,把結論寫回文件 | 使用者, agent |
| `mreq-apply` | 逐項實作文件的 Tasks,更新 checkbox 和 Handoff | 使用者, agent |
| `mreq-close` | 核對程式碼與文件,通過後刪除文件 | 只有使用者 |
| `mreq-how` | 先確認問題的解讀,再產生解說程式碼的離線 HTML,附 Mermaid 圖表與圖例,放在 session root 的 `.mreq/how/`. 加 `--plain` 改寫給企劃, PM 等非程式人員: 用功能名詞, 不放程式碼位置 | 只有使用者 |
| `mreq-graph` | 先確認描述的解讀,再把描述畫成 Mermaid 圖表,產生附圖例的離線 HTML,放在 session root 的 `.mreq/graph/` | 只有使用者 |
| `mreq-shared` | 不執行任何任務. 放其他 skill 共用的 script, template, Pele, 與 Mermaid 規則 | 沒有人 |

「誰能呼叫」只適用 Claude Code. 其他 agent 不讀 `disable-model-invocation`, 模型可能自動觸發任何一個 skill. `mreq-close` 核對通過後會直接刪除文件.

典型流程: `/mreq-define` → (`mreq-grill`) → `mreq-apply` → commit (程式碼和 `.mreq/`) → `/mreq-close`.

skill 之間能自動接續的地方, 會用選項問你下一步, 不需要輸入指令: `mreq-define` 可接 `mreq-grill` 或 `mreq-apply`, `mreq-grill` 與 `mreq-apply` 可互相接續, `mreq-close` 發現未完成的 task, 失敗的測試或要修正的 finding 時, 可帶著它們接 `mreq-apply`. 「只有使用者」能呼叫的 skill 不會被自動接續, 這時 skill 會給出完整的指令讓你執行.

Claude Code 有 `AskUserQuestion` 時, 每個問題都用選項回答. 選項沒有你要的答案時, 在選項下方的文字欄輸入.

`mreq-apply` 不會自己 commit. `mreq-close` 刪除前不檢查 git 狀態, 也不詢問. 要保留文件內容, 請先 commit, 再執行 `/mreq-close`.

建議在新的 session 執行 `/mreq-close`. 同一個 session 做過修改時, 它的檢查不獨立. 這時 `mreq-close` 會先說明, 並問你要繼續還是停下.

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
├── mreq-how/     # SKILL.md, EXPLORER.md, WRITING.md, skeleton.html, page.py
├── mreq-graph/   # SKILL.md, WRITING.md, skeleton.html, page.py
└── mreq-shared/  # 共用: scripts/mreq.py, templates/, scripts/check.mjs, vendor/ (Pele), MERMAID.md
```
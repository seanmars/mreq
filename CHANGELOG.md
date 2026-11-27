# Changelog

## Unreleased

### Added

- `mreq-apply` 的 orchestrate 模式: `/mreq-apply [<path>] --orch`. 主 agent 是 orchestrator, 只管理文件. 每個 phase 由一個 subagent 實作, 再由另一個 subagent 驗證.
  - 開啟方式: 輸入有 `--orch`, 或使用者在對話裡用自己的話要求這個模式 (例: "orch mode", "用 orchestrator", "交給 subagent 做"). 這些字只出現在文件, findings 或工作的主題時不開啟. 無法判斷時不開啟. 開啟時, 進度訊息會說明.
  - phase 是 `## Tasks` 裡一個 `### ` 標題底下的 task. 第一個標題之前的 task 自成一個 phase. 沒有標題時, 全部 task 是一個 phase.
  - `refactor` 文件的 pin task (第一個 task) 永遠自成一個 phase. 文件把其他 task 放在同一個 phase, 或沒有標題時, orchestrator 把那個 phase 拆成兩個: 先 pin task, 再其他 task. verifier 在整個 phase 完成後才檢查, 所以 pin 與修改在同一個 phase 時, 它無法在修改前的程式碼上執行 pin.
  - 只有 orchestrator 寫文件: 打勾, `## Handoff`, `## Root Cause`, `## Open` 與 `update`. implementer 與 verifier 不修改 `.mreq/` 的任何檔案.
  - implementer 讀 `IMPLEMENTER.md`, verifier 讀 `VERIFIER.md`. verifier 只拿到文件路徑, phase 與 implementer 修改的檔案清單, 不拿到 implementer 的結論.
  - verifier 判定 `pass` 時, orchestrator 才把這個 phase 的 task 打勾. 判定 `fail` 時, finding 交給 implementer 修正. 同一個 phase 驗證失敗兩次時, 問使用者: 再試一次, 自己實作, 或停止.
  - subagent 不能問使用者. implementer 遇到問題時停止並回報, orchestrator 問使用者後再派發.
  - orchestrator 不讀程式碼, 不執行專案的程式碼. 最後一個 verifier 的測試結果就是 `done` 的依據, 不重跑.
  - agent 不能 spawn 可以寫入檔案的 subagent 時, 改用一般模式.

### Changed

- `mreq-define` 寫文件時, task 可以分成能各自檢查的階段時, 用 `### <phase 名稱>` 標題分組. task 編號跨 phase 連續. 4 個 task 以下, 或沒有這種階段時, 不寫標題. `refactor` 是例外.
- `refactor` 的 template 有兩個 phase 標題: `### Pin` 與 `### Refactor`. `mreq-define` 一律保留這兩個標題, 並改用文件的語言命名: pin task 單獨在第一個 phase, 修改程式碼的步驟在之後的 phase.
- `mreq-grill` 修改 `## Tasks` 時保留 `### ` 標題, 新 task 放在所屬的 phase 底下. `refactor` 文件的 pin task 保持單獨一個 phase.
- `mreq-apply` 收到 `mreq-close` 的 findings 時, 文件有 `### ` 標題的話, 把 findings 放在最後一個新標題底下.
- `mreq-apply` 的 `argument-hint` 改為 `[<path>] [--orch]`.

## 0.26.0

### Changed

- `mreq-define` 可以直接使用 `mreq-pro` 或 `mreq-terms` 的結果. 對話裡有其中一個的結果, 而且使用者沒有給需求 (或給的就是那個新 prompt) 時, 需求是最新一個結果裡的 prompt, 加上使用者之後要求的修改. 結果已經回答的事不重新回答, 也不問使用者. 重述時術語保留原文.
- 結果來自 `mreq-terms` 時:
  - Step 3 問它列出的 "沒提到的事", 對話裡已經決定的不問. 沒有使用者的回答, 不加進範圍.
  - prompt 可能是不只一個問題時, 它選定的那一個寫進 Assumptions, 除非使用者已經確認.
  - 它說不適合的術語不使用, 改用它給的術語.
- 結果來自 `mreq-pro` 時:
  - 不重新回答四題.
  - Step 1 照常讀程式碼. `mreq-pro` 不讀程式碼, 所以它的答案與程式碼衝突時, 以程式碼為準, 並在重述時說明.
  - Step 3 問 `mreq-pro` 留給使用者, 而且對話裡還沒回答的問題. 要用 prototype 決定的選擇不問使用者.
  - Step 4 保留 prompt 的方法, 工具與 pass/fail 條件, 不改寫成 agent 自己的話. pass/fail 條件寫進 Goal. crux 的做法, 原始資料, 方法與工具, 要 prototype 的選擇寫進 Decided. 刪除或縮小的部分寫進 Out of scope.
  - 每個要 prototype 的選擇是一個 task, 排在依賴它的 task 之前. pass/fail 條件是最後一個 task 的檢查方式.
- `mreq-define` 的 `argument-hint` 改為 `[<request>]`.
- `mreq-pro` 的結尾多一行提示: 接著輸入 `/mreq-define` (不給需求), 就會用新 prompt 開始工作.
- `mreq-terms` 結尾的提示多一個下一步: `/mreq-define` (不給需求).
- `docs/mreq-flow.html` 的 skill 交接圖補上缺少的交接: `mreq-terms` 與 `mreq-pro` 的提示, `mreq-define` 與 `mreq-close` 只給出 `/mreq-apply <path>` 的情況, 以及 `mreq-apply` 在 template 文件選 `Stop` 的情況.
- `docs/mreq-flow.html` 對照每個 skill 的檔案重寫.
  - 新增: 8 個 skill 的一覽表與常見的走法; "需求的來源" 一節; `mreq-close` 哪些檢查要執行的圖; "頁面與 build" 一節; 各 skill 確認題的對照表, 以及各 skill 被拒絕時另外做的事.
  - 修正: Claude Code, Grok 與 Antigravity 都讀 `disable-model-invocation`, 不是只有 Claude Code.
  - 修正: `mreq-define` 的 Step 5 補上 `feature` 的 `In:`; `mreq-grill` 的入口補上焦點與路徑的判斷.
  - 修正: 典型 session 裡, `mreq-close` 不重跑 `mreq-apply` 已經驗證的測試指令與 task 檢查.
  - 修正: `Unknown skill` 只用指出的名稱重試一次; `mreq-how` 的 explorer 也不執行專案程式碼.
  - 刪除 skill 沒有寫的說法, 例: "完成時不提醒 commit".

## 0.25.0

### Added

- `mreq-terms`: 使用者有想法, 但缺少專家的術語與知識時使用. 只有使用者能呼叫: `/mreq-terms [<prompt>]`.
  - 從使用者的情境開始: prompt, 對話裡已有的內容, 以及 prompt 提到的檔案與程式碼. 每個術語都要對應到這些材料.
  - prompt 可能是不只一個問題時, 先列出 2 到 3 個問題, 每個附一個術語與分辨它的跡象.
  - 給出 5 到 12 個術語: 意思, 對應的部分, 專家知道而使用者該知道的事, 一個附連結的實際案例, 能向 agent 要求什麼.
  - 另外給出: 看起來對但不適合的術語, 2 到 3 個相鄰領域, 使用者沒提到但該在意的事.
  - 最後用術語改寫 prompt. 只換用詞, 不改變工作內容.
  - 每個連結都要打開確認; 無法確認的引用要刪除. 不自創術語. 兩個社群用詞不同時, 兩個都給.

### Changed

- `mreq-pro` 回到 0.23.0 的流程: 四題, 新 prompt, 刪除清單. 它不再教術語, 不讀檔案, 也不打開網頁. 0.24.0 加入的術語流程移到 `mreq-terms`.
- `mreq-pro` 沒有收到 prompt, 而且對話裡有 `mreq-terms` 的結果時, 改寫那個結果裡的 prompt (最新的一個, 加上使用者之後要求的修改). 它保留術語, 並把 `mreq-terms` 列出的 "沒提到的事" 放進給使用者的問題, 不放進工作內容. `mreq-terms` 的結尾會提示這個用法.

### Removed

- `mreq-pro` 的 `--no-terms`. `argument-hint` 改回 `[<prompt>]`.

## 0.24.0

### Changed

- `mreq-pro` 預設會教術語, 並用術語改寫 prompt.
  - 從 prompt 與它提到的檔案和程式碼開始, 不從摘要開始.
  - prompt 可能是不只一個問題時, 先列出 2 到 3 個問題, 每個附一個術語與分辨它的跡象. 然後選最可能的一個, 並說明原因.
  - 四題之後多三題: 8 到 12 個術語 (意思, 對應 prompt 的哪一部分, 一個附連結的實際案例, 能向 agent 要求什麼), 2 到 3 個相鄰領域, 使用者沒提到但該在意的事.
  - 每個連結都要打開確認. 無法確認的引用要刪除. agent 沒有開網頁的 tool 時, 不給引用.
  - 新 prompt 用術語取代原本的白話描述, 但不能因為術語而增加工作. 沒提到的事只能列為給使用者的問題.
  - 結尾多一份清單: 哪個片語換成了哪個術語.
- `mreq-pro` 加上 `--no-terms`: 跳過上面三題, 不打開網頁, 只在看不懂 prompt 時才讀檔案. `argument-hint` 改為 `[--no-terms] [<prompt>]`.

## 0.23.0

### Changed

- 每個 skill 都帶著自己需要的檔案, 不再讀取其他 skill 的目錄. 可以只安裝部分 skill.
  - `mreq-define`, `mreq-grill`, `mreq-apply`, `mreq-close` 各有一份 `scripts/mreq.py`. `mreq-define` 另有 `templates/`. `mreq-define` 與 `mreq-grill` 各有一份 `GRILL.md`.
  - `mreq-how` 與 `mreq-graph` 各有一份 `scripts/page.py`, `scripts/check.mjs`, `vendor/` (Pele) 與 `MERMAID.md`.
  - script 的路徑是 `${CLAUDE_SKILL_DIR}/scripts/<script>`, 不再有 `/../mreq-shared`. `page.py` 的第一個參數仍然是 `how` 或 `graph`.
- `page.py` 只讀自己 skill 的 `skeleton.html`. 參數與 skill 不符時 (例: 用 `mreq-how` 的 `page.py` 執行 `graph build`), build 失敗, 並指出要用哪一個 skill 的 `page.py`.
- 只有 `mreq-define` 的 `mreq.py` 能執行 `new`. 其他 skill 的 `mreq.py` 沒有 `templates/`, 執行 `new` 時會指出要用 `mreq-define` 的 script.
- 交接的目標 skill 沒有安裝時, skill 告知使用者要安裝哪一個 skill, 然後停止.
- 多個 skill 使用的檔案放在 repository 的 `shared/`. `tools/sync.py` 把它們複製到各 skill; `tools/sync.py --check` 與測試會檢查每份複本和來源相同.

### Removed

- `mreq-shared` skill. 用 `npx skills` 安裝過舊版時, 先執行 `npx skills update`, 再執行 `npx skills remove mreq-shared` (安裝時用了 `-g` 就加 `-g`). 順序不能反過來: 舊版的 skill 還需要 `mreq-shared`. 留著不會造成錯誤, 但沒有 skill 會使用它. 用 Claude Code plugin 安裝時, 只需要更新 plugin.

## 0.22.0

### Added

- 只限使用者呼叫的 skill (`mreq-define`, `mreq-close`, `mreq-how`, `mreq-graph`, `mreq-pro`, `mreq-shared`) 加上 `agents/openai.yaml`, 內容是 `allow_implicit_invocation: false`. Codex 不讀 `disable-model-invocation`, 改讀這個設定.
- `mreq-shared` 加上 `disable-slash-command: true`. Antigravity 用這個設定把它從 slash command 中移除.
- `mreq-pro` 加上 `argument-hint`. agent 沒有替換 `$ARGUMENTS` 時, prompt 就是使用者在呼叫 skill 時給的文字.
- `.gitattributes` 讓文字檔一律使用 LF.

### Changed

- 新的共用段落 "Running another mreq skill" (`mreq-define`, `mreq-grill`, `mreq-apply`, `mreq-close`): 交接到另一個 skill 時:
  - 有 skill tool 的 agent (Claude Code), 用 skill 清單裡顯示的名稱呼叫. 用 plugin 安裝時是 `mreq:mreq-apply`. 收到 `Unknown skill ... Did you mean` 時, 用建議的名稱重試一次.
  - 沒有 skill tool 的 agent (Codex, Grok, Antigravity), 讀取 `../mreq-<name>/SKILL.md` 並照著執行.
  - 只有在呼叫被拒絕之後, 才禁止自己讀取 SKILL.md.
- 只限使用者呼叫的 skill 接受每種呼叫方式: `/mreq-x`, `/mreq:mreq-x`, Codex 的 `$mreq-x`, 或直接點名. 原本只接受 `/mreq-x`.
- 給使用者的指令依照 agent 的寫法: Codex 寫 `$mreq-close <path>`, 其他 agent 寫 `/mreq-close <path>`.
- "Asking the user" 列出各 agent 的提問 tool (`AskUserQuestion`, `ask_user_question`, `ask_question`, `request_user_input`). 一個問題的選項比 tool 能接受的多時, 這一題改用純文字提問. tool 回傳錯誤後, 這個對話的其餘問題都改用純文字.
- 只有 Claude Code 會附上 allow rule. 其他 agent 只回報被拒絕的指令或路徑.
- explorer subagent 列出各 agent 的類型: Codex 的 `explorer`, Grok 的 `explore`, Antigravity 的 `research`.
- README 依 agent 列出安裝指令, 安裝位置與呼叫方式.

### Fixed

- 用 plugin 安裝時, skill 交接會先出現 `Unknown skill: mreq-apply` 失敗, 然後才用 `mreq:mreq-apply` 重試成功.
- 在 Codex, Antigravity, 以及 Grok 的交接中, `${CLAUDE_SKILL_DIR}` 不會被替換, 所以 script 指令會失敗. 現在 skill 要求在執行第一個指令之前自行替換成絕對路徑. 任何還含有 `${` 的指令都不能執行.
- 共用檔的路徑改用 `${CLAUDE_SKILL_DIR}` 寫成完整路徑: `GRILL.md`, `MERMAID.md`, `WRITING.md`, `EXPLORER.md`, 以及交接時讀取的 SKILL.md. 原本寫 "`../mreq-shared` from this skill's directory", 要由 model 自己組出路徑, 可能被當成相對於專案根目錄. 「不使用含有 `${` 的路徑」的規則也擴大到讀檔. `WRITING.md` 不會被替換變數, 所以改成以 SKILL.md 給的路徑為準.
- 其他 agent 沒有替換 `${CLAUDE_SKILL_DIR}` 時, skill 會說明去哪裡找 SKILL.md 的路徑: Codex 的 `<path>`, Grok skill 清單的 `Absolute path`, 或 model 自己讀檔時用的路徑. 錯誤訊息中的路徑以 `/../mreq-shared` 開頭時, 表示變數是空的, 要補上路徑後重新執行. script 路徑不存在 (`Failed to spawn`, `can't open file`) 不是換用 `python` 的理由.
- sandbox 封鎖 `uv` 時, 每個 script 指令都會先失敗一次. 現在第一次成功的 runner 會用在同一個對話的其餘指令. Windows 上 Microsoft Store 的 `python3` stub 也視為找不到.

## 0.21.0

### Added

- `mreq-pro`: 改寫 prompt, 要求頂尖專家的做法: 更深, 不是更大. 先簡短回答四個問題: 關鍵難點, 原始資料, 方法與工具, 事先定義的外部驗證. 不了解領域時, 詢問使用者, 不猜測. 再把新 prompt 放在一個 code block. 新 prompt 的範圍不大於原本的 prompt, 要求 agent 用實驗決定能實驗的選擇, 並把產品或偏好的選擇列為問題. 最後逐行列出刪除或縮小的部分與原因. 只有使用者能呼叫: `/mreq-pro [<prompt>]`.

## 0.20.0

### Changed

- `mreq-close` 核對 `done` 的文件時, 如果 `## Handoff` 寫了驗證方式, 不再重跑測試指令與 task 自己的檢查, 也不從 README 或 agent 指示檔找測試指令. `mreq-apply` 只在 task 全部勾選而且相關測試通過時才設定 `done`. Handoff 只寫完成, 沒寫怎麼驗證時, 不適用. `issue` 的 repro 與 `refactor` 的 Behavior Pin 仍會執行. 報告會寫出沒重跑的檢查與 Handoff 寫的驗證方式, 不算通過.

## 0.19.0

### Added

- `mreq-grill` 第一輪可以指定焦點: `/mreq-grill [<path>] [<focus>]`, 例: `/mreq-grill <path> 錯誤處理`. 四象限仍然全部掃描. 每個象限先處理焦點, 問得更深, 並先回報焦點的發現. 第一個字是 `.mreq/` 底下的檔案路徑時, 它是文件路徑, 其餘是焦點; 否則整段輸入都是焦點. 規則寫在 `mreq-shared/GRILL.md` 的 "A focus", 所以 `mreq-define` 的 "先 grill, 不寫文件" 也適用.

### Changed

- `mreq.py progress` 多印一行 `Status: <status>`. front matter 的 `status` 或 `schema` 不合法時, 再多印 `Warning:` 行. 只安裝部分 skill 時, 必須同時更新 `mreq-shared`.
- `mreq-apply` 從 `progress` 的 `Status:` 行取得 status. 使用者給路徑時, 不再另外執行 `list`. `progress` 印出 `Warning:` 行時, 在進度訊息裡告訴使用者.
- `mreq-define` 把 "需求只是在問程式碼怎麼運作" 的詢問 (`Explain it` 或 `Treat it as a task`) 從 Step 2 移到 Step 1 的開頭. 它在執行任何指令或讀任何程式碼之前發生, 只依照需求的文字判斷.
- `mreq-close` 的 Step 1 與報告, `mreq-how` 的報告改為清單格式. 規則內容不變.
- 用詞統一: 挑選文件時一律寫 "Never pick one yourself"; `mreq-how` 與 `mreq-graph` 的 "Before the yes" 改為 "Before the user confirms".

### Fixed

- `mreq-define` 寫 `feature` 文件時, 補上 `## Scope` 的 `In:` 要寫什麼. 原本只有 `Out:` 的規則, 但 `mreq-apply` 只實作 `In:` 列入的範圍.
- `mreq-define` 不寫文件的流程: `issue` 兩次修正失敗後, 補上 "先說明並重新驗證 root cause, 再做第三次修正", 與 `mreq-apply` 一致.
- `mreq-how` 的 explorer 補上不可執行專案的程式碼, 與 `mreq-how` 的 Guardrails 一致.
- `mreq-apply` 的 description 補上 `mreq-grill` 的交接; `mreq-grill` 的 description 補上 `mreq-apply` 的交接.

## 0.18.0

### Changed

- `mreq-close` 讓使用者挑選文件時, 每個選項的 label 開頭用方括號標示文件的 status, 例: `[done] add login retry`. `done` 的文件排前面, 其他文件依 `list` 順序排在後面.

## 0.17.0

### Changed

- `mreq-grill` 確認重述的選項改為: "Correct, write it into the document, then implement" (推薦), "stop here", "then keep grilling", "Something is wrong". "then keep grilling" 取代 "Grill more": 先把已確認的結論寫回文件, 再自動開始下一輪, 不需要重新執行 `/mreq-grill`. 要繼續 grill, 一定先寫回, 所以已確認的結論不會只留在對話裡. Discuss only 不寫回文件, 選項是 "Correct, stop here", "Correct, keep grilling" 與 "Something is wrong".
- `mreq-grill` 每次重述都包含文件還沒有的全部內容. 寫回之後, 只重述之後各輪的變更. 還沒寫回時 (例: 選了 "Something is wrong" 之後), 仍然完整重述. 所以選 "Correct" 只確認最後一次重述, 寫回的內容就是那一次重述.
- 同一個對話再 grill 同一個對象時, 只做差異 (`mreq-shared/GRILL.md` 的 "A later round"). 只掃上一輪改變的項目, 仍未決的項目與使用者指定的焦點. 已成立的主張與已確認的前提不重新驗證. 只回報有新發現的象限. `mreq-define` 的 "先 grill, 不寫文件" 適用同樣的規則. 使用者要求時仍然做完整的掃描; 新的對話一律從完整的掃描開始.
- `mreq-grill` 在同一個對話再次處理同一份文件時, 重讀文件, 但只重讀有變更的程式碼.

## 0.16.0

### Changed

- `mreq-define` 確認重述的那一題同時選下一步, 寫完文件後不再問 "Implement / Pressure-test / Stop here". 一般需求的選項: "Correct, write the document, then implement" (推薦), "then grill it", "write the document only", "Something is wrong". 計畫還沒被檢驗時, 推薦 "then grill it". 選項沒有的下一步在文字欄輸入.
- `mreq-define` 遇到小需求 (Simple 而且沒有延後的決策) 時, 推薦 "Correct, implement now, no document". 選項順序: "implement now, no document", "grill it first, no document", "write the document, then implement", "Something is wrong".
- `mreq-define` 在使用者明確要求跳過確認時, 寫完文件就給出路徑並停止, 不再問下一步.
- `mreq-grill` 確認重述的那一題同時選下一步, 寫回文件後不再詢問. 選項: "Correct, write it into the document, then implement" (推薦), "stop here", "Grill more", "Something is wrong". "Grill more" 在寫回文件之前繼續 grill.
- `mreq-close` 沒有指定路徑時, 如果只有一份 `done` 的文件, 而且沒有 `warning` 或 `error`, 直接核對那一份, 不再詢問.
- `mreq-close` 找不到測試指令 (文件, README 與 agent 指示檔都沒有) 時不再詢問 "Close anyway / Keep it", 只在報告寫出沒有執行測試. 這不算通過. 指令被拒絕時仍然詢問.
- `mreq-close` 交給 `mreq-apply` 前, 不再提醒修正並 commit 後再執行 `/mreq-close`. 選了 Stop 或 Keep it 時, 只給出 `/mreq-apply <path>` 與要修的項目.
- `mreq-apply` 的進度兩行每次執行只顯示一次. 使用者回答問題後繼續工作的回合, 不再執行 `progress`.
- `mreq-how` 與 `mreq-graph` 的報告不再詢問 "Open it / Don't open", 只給出頁面路徑. 使用者要求時才開啟頁面.
- `mreq-define`, `mreq-grill`, `mreq-how`, `mreq-graph` 確認時, 不再提示可以在文字欄輸入修正. 在文字欄輸入的修正仍然照常處理.
- `mreq-define` 只寫文件後停止時, 只給出文件路徑. 不寫文件的報告, 不再說明沒有文件可以 close.

## 0.15.1

### Changed

- `mreq-apply` 完成所有 task 後, 只提示 `/mreq-close <path>`, 不再提醒先 commit.

## 0.15.0

### Changed

- `mreq-apply` 沒有指定文件時, 如果 `list --open` 只有一份文件, 而且沒有 `warning` 或 `error`, 直接實作那份文件, 不再詢問. 文件路徑由 `progress` 的 `Using:` 行顯示.
- `mreq-grill` 沒有指定文件時, 適用同樣的規則: 只有一份開啟中的文件時直接 grill, 不再詢問. 開始前先說明文件的標題與絕對路徑.

## 0.14.1

### Changed

- `mreq-apply` 與 `mreq-close` 找不到文件時, 說明後停止. `mreq-apply` 建議用 `/mreq-define` 開始新工作.
- `mreq-grill` 選了 Discuss only 之後, "Correct, stop here" 直接給出文件路徑並停止, 不再問下一步.
- `mreq-close` 測試失敗時, 多一個 "Close anyway" 選項. 測試失敗, 測試沒執行與 finding 的問題一起問, 測試的問題排前面. 選了 Stop 或 Keep it 之後, 不再問剩下的問題. 依序處理答案: 任一 Stop 或 Keep it 就停止; 否則任一 Fix 就交給 `mreq-apply`; 否則刪除文件. 失敗的測試只在選了 Fix now 時才交給 `mreq-apply`.
- 流程頁補上漏畫的詢問點: `mreq-define` 的 "Continue it" 與 "Explain it", `mreq-grill` 象限 2 與 3 的提問, `mreq-how` 對未知 `--xxx` 的讀者詢問.

## 0.14.0

### Changed

- `mreq-close` 不再要求, 也不再建議新的 session. 同一個 session 做過修改時, 不再詢問 "Continue here" 或 "Stop", 直接核對. `mreq-apply` 與 `mreq-close` 提示 `/mreq-close` 時, 不再建議新的 session. 核對仍然只依照現在讀到的文件與程式碼, 不依照對話記憶.

## 0.13.0

### Added

- `mreq-define` 新增不寫文件的流程. 需求是 Simple 而且沒有延後的決策時, 確認重述的第二個與第三個選項換成 "Correct, implement now, no document" 與 "Correct, grill it first, no document". 選了直接實作之後, 在同一個 session 實作, 結束時對照重述回報, 不需要 `/mreq-close`. 選了先 grill 之後, `mreq-define` 自己對重述做四象限 grill, 不寫檔案, 然後再重述一次. 使用者也可以在文字欄要求不寫文件; 這時不看需求大小. 工作超出重述的範圍或中途停止時, 會補寫文件, 之後用 `mreq-apply` 接續.

### Changed

- grill 的方法 (四象限, 訪談規則, 限制) 移到 `mreq-shared/GRILL.md`. `mreq-grill` 與 `mreq-define` 都讀這一份. 只安裝部分 skill 時, 必須同時更新 `mreq-shared`.

## 0.12.0

### Added

- `mreq-define` 確認重述時, 多一個 "Correct, write the document, then implement" 選項. 選了之後, 寫完文件就直接接 `mreq-apply`, 不再多問一次下一步.
- `tests/`: `mreq.py` 與 `page.py` 的單元測試, 各 SKILL.md 共用段落的一致性檢查, 版本號檢查. 執行 `python -m unittest discover -s tests`.

### Changed

- `mreq-how` 與 `mreq-graph` 共用 `mreq-shared/scripts/page.py`. 第一個參數是 `how` 或 `graph`, 例如 `page.py how new <slug>`. 各 skill 目錄下的 `page.py` 已移除. 只安裝部分 skill 時, 必須同時更新 `mreq-shared`.
- 每個 skill 都用 `uv run "${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/<script>"` 執行 script. script 的路徑一律加雙引號. 所有路徑都用 `/`, Windows 也一樣.
- `mreq-apply`: 文件是 `done`, task 全部勾選, 而且沒有 findings 時, 說明已完成並給出 `/mreq-close <path>`, 然後停止. `done` 但還有未勾選的 task 時, 先設回 `active` 再繼續.
- `mreq-close`: "Tests not rerun" 改名為 "Tests already run by a task", 避免和 "Tests not run" 混淆.
- `page.py` 移除沒有 skill 使用的 `dir` 指令.

### Fixed

- `page.py` 在 Windows 印出的路徑改用 `/`. 原本的反斜線路徑沒加引號貼進 Git Bash 時, 反斜線會消失.
- `page.py` 的錯誤訊息改指向 `MERMAID.md`. figure 與顏色的規則在那裡, 不在 `WRITING.md`.
- `mreq-grill`: 補上 `update` 之後要再讀一次文件, 和 `mreq-apply` 相同.
- `plugin.json` 補上 description, 並修正 keywords.

## 0.11.1

### Added

- 輸入 slash command 時顯示參數提示 (`argument-hint`): `/mreq-how [--plain] <question>`, `/mreq-define <request>`, `/mreq-graph <description>`, `/mreq-apply`, `/mreq-grill`, `/mreq-close` 顯示 `[<path>]`.

## 0.11.0

### Added

- `mreq-how` 新增 `--plain` style: `/mreq-how --plain <問題>`. 頁面寫給企劃, PM 等不讀程式碼的人: 用功能名詞解說, 列出規則與數值, 不放路徑, `path:line` 和程式碼名稱. 內容仍然逐一對照程式碼確認. 沒加 style 時維持原本的工程師版. 不認得的 `--` 參數會用選項詢問讀者是誰.

## 0.10.0

### Changed

- `mreq-close` 不再重跑 `mreq-apply` 已跑過的測試指令. 條件: 有已勾選的 task, 而且它的工作就是跑相關測試 (例: `issue` 的 "Run the related tests"). 只說明檢查方式的 task, 或未勾選的 task, 不算. repro, Behavior Pin 與 task 自己的檢查仍會執行. 報告會寫出沒重跑的指令與 task 編號.

## 0.9.0

### Changed

- 每個 skill 都用 `AskUserQuestion` 的選項提問: 每題 2 到 4 個選項, 推薦答案排第一. 選文件, 確認解讀, 是否開啟網頁, build 失敗後的處理, 都改成選項. 選項沒有的答案, 在選項下方的文字欄輸入.
- `mreq-define` 與 `mreq-grill` 確認重述時, 多一個 "Something is wrong" 選項, 用多選標出有誤的項目. 訪談可以選 "Decide later" 或 "Leave it open".
- skill 之間改用 Skill tool 直接接續, 不需要輸入指令: `mreq-define` 繼續舊文件時接 `mreq-apply`; `mreq-apply` 選 "Grill first" 時接 `mreq-grill`; `mreq-close` 發現未完成的 task, 測試失敗或選 "Fix the code" 時, 帶 findings 接 `mreq-apply`, 而且不刪除文件.
- 「只有使用者」能呼叫的 skill (`mreq-define`, `mreq-close`, `mreq-how`, `mreq-graph`) 仍要手動輸入. skill 會給出填好參數的完整指令.

## 0.8.0

### Breaking

- `mreq-do` 改名為 `mreq-define`. 請改用 `/mreq-define <需求>`. 舊名稱 `do` 容易被理解成"直接實作", 但這個 skill 只負責定義需求並產生任務文件.

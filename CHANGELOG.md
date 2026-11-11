# Changelog

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

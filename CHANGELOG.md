# Changelog

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

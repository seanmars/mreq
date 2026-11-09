# Changelog

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

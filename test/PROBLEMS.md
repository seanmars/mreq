# 測試題目

每題有兩份檔案:

- `request.txt`: 使用者對 agent 說的需求. agent 看得到.
- `intent.md`: 意圖卡, 寫出使用者心中的答案. 只有模擬使用者看得到.

hidden test 依意圖卡評分. 測試方式見 [README.md](README.md).

## 選題原則

- **需求刻意模糊**: 只說功能, 不說邊界規則. define 要問對問題, 或在 restate 中寫出假設讓使用者糾正, 最終程式碼才會正確.
- **包含多義詞**: 例如 "第二件", "滿額", "空檔". 這些詞可以有兩種以上的讀法.
- **API 名稱固定**: 需求指定檔名, 函式名稱和參數, 讓 hidden test 能直接 import.
- **可以差分測試**: 每題都有參考實作, 能用大量隨機輸入比對結果.
- **有一題對照組**: 用規格明確的題目, 確認新規則不會讓明確規格的題目變差.

一開始用了 4 題 LeetCode (68, 460, 10, 591), 但效果不好. model 早就背熟這些題目, 需求也寫得很完整, define 幾乎不需要追問, 結果只剩 token 差異. 所以正式測試只保留 591 當對照組, 另外加入 3 題模糊需求.

| 題目 | 類型 | 模組 | 規則案例 | 隨機案例 | 效能案例 |
|---|---|---|---|---|---|
| checkout 購物車結帳 | 模糊需求 | `checkout.total` | 22 | 3000 | 無 |
| sla 工單到期時間 | 模糊需求 | `sla.due_at` | 21 | 3000 | 無 |
| booking 會議室預約 | 模糊需求 | `booking.BookingBook` | 22 | 3000 | 無 |
| tagval Tag Validator | 對照組 (LeetCode 591) | `tag_validator.is_valid` | 32 | 3000 | 1 |
| justify, lfu, regex | pilot (LeetCode 68, 460, 10), 正式測試不使用 | 見下文 | | | |

---

## checkout: 購物車結帳

### 需求 (`request.txt`)

> 新增 checkout.py,提供 total(items: list[dict], coupon: str | None = None) -> int,計算購物車的應付金額. items 每一項有 sku, name, price (單價,整數元), qty (數量), category. 促銷規則: 飲料 (category 是 "drink") 第二件六折; 優惠券 "SAVE100" 滿 1000 折 100; 優惠券 "OFF10" 全館九折. 運費 60 元,滿 499 免運. 要附上測試.

### 意圖卡 (`intent.md`)

- 第二件六折: 只在同一個 sku 之內配對. 同一個 sku 的數量 n, 其中 floor(n/2) 件用六折, 其餘原價. 不同 sku 的飲料不互相配對. items 裡出現相同 sku 的多個項目時, 先合併數量再配對.
- 金額計算過程保留精確值, 只在最後算出應付金額時四捨五入成整數一次. 四捨五入是 0.5 進位 (22.5 → 23), 不是銀行家捨入.
- 計算順序: 先算商品折扣, 再套優惠券, 最後算運費.
- SAVE100 的門檻用商品折扣後的金額判斷, 剛好 1000 也算滿額. 沒達門檻時優惠券無效但不報錯.
- OFF10 是商品折扣後的金額打九折.
- 優惠券不折運費.
- 免運門檻用套用優惠券之後的精確值判斷, >= 499 免運, 否則加 60.
- 購物車是空的, 或所有 qty 都是 0: 應付金額 0, 不收運費.
- 不認得的優惠券代碼 (大小寫完全比對): 丟 `ValueError`. `None` 表示沒有優惠券.
- qty 或 price 是負數: 丟 `ValueError`. qty 是 0 的項目忽略.

### 陷阱

| 陷阱 | 常見的錯誤 |
|---|---|
| "第二件" 的配對範圍 | 跨 sku 配對, 或沒有合併相同 sku 的多個項目 |
| 捨入時機與方式 | 每一步都四捨五入, 或用 Python `round()`: `round(82.5)` 得到 82, 不是 83 |
| 門檻用哪個金額 | 用原價判斷 SAVE100, 或用優惠券前的金額判斷免運 |
| 精確值與門檻 | 498.6 先四捨五入成 499 才判斷, 結果誤判為免運 |
| 空購物車 | 照字面收 60 元運費 |

### Hidden test 規則案例

`second-item same sku only`, `second-item floor(n/2)`, `second-item merge same sku`, `second-item non-drink`, `round half up once` (2 個案例), `round once not per step`, `SAVE100 threshold after item discount`, `SAVE100 inclusive 1000`, `SAVE100 below threshold no error`, `OFF10 after item discount`, `coupon not on shipping`, `free shipping after coupon`, `free shipping inclusive 499`, `free shipping exact not rounded`, `empty cart`, `all qty zero`, `unknown coupon ValueError`, `coupon case-sensitive`, `negative qty ValueError`, `negative price ValueError`, `qty zero ignored`.

### 隨機案例

每組隨機產生 6 個 sku. 單價從 5, 15, 25, 35, 45, 99, 120, 250, 333, 499, 550 中挑選. 這些單價打六折或九折後容易出現 .5. 類別中飲料占一半. 購物車有 0 到 5 個項目, 可能包含相同的 sku, 每項 qty 0 到 5. 優惠券是 `None`, `SAVE100` 或 `OFF10`, 其中 `None` 機率加倍. 參考實作用 `Fraction` 計算精確值.

---

## sla: 工單 SLA 到期時間

### 需求 (`request.txt`)

> 新增 sla.py,提供 due_at(created: datetime, hours: float, holidays: set[date] = frozenset()) -> datetime,計算客服工單的 SLA 到期時間. 只算上班時間: 週一到週五 09:00 到 18:00,中午 12:00 到 13:00 午休不算. holidays 裡的日期整天不上班. 要附上測試.

### 意圖卡 (`intent.md`)

- 上班時段是 09:00-12:00 和 13:00-18:00 (週一到週五, 排除 holidays). 時段是半開區間: 剛好 12:00 或 18:00 不算在時段內.
- 工單在上班時段外建立 (下班後, 週末, 假日, 午休, 或剛好 12:00 / 18:00): 從下一個上班時段的開始時間起算.
- 到期時間剛好落在時段結束時: 回傳那個結束時間 (例如 18:00), 不跳到下一個時段的開始.
- hours 是 0: 回傳起算時間 (調整後的起點).
- hours 可以有小數. created 的秒數照樣保留.
- hours 是負數: 丟 `ValueError`.
- created 是 naive datetime, 不處理時區.

### 陷阱

| 陷阱 | 常見的錯誤 |
|---|---|
| 剛好在時段結束時到期 | 回傳隔天 09:00, 而不是當天 18:00 |
| 在 12:00 或 18:00 整點建立 | 把整點當成時段內, 從 12:00 開始算 |
| `hours = 0` | 直接回傳 `created`, 沒有調整到上班時段 |
| 在午休, 週末或假日建立 | 從 `created` 開始算, 沒有跳到下一個時段 |

### Hidden test 規則案例

`inside window simple`, `lunch skipped`, `ends exactly 18:00`, `ends exactly 12:00`, `created after hours`, `created before hours`, `created during lunch`, `created exactly 12:00`, `created exactly 18:00`, `weekend skipped`, `created on weekend`, `holiday skipped`, `created on holiday`, `zero hours inside`, `zero hours outside`, `zero hours at 12:00`, `fractional hours`, `seconds kept`, `multi-day span`, `negative ValueError`, `default holidays` (不傳 holidays 參數).

### 隨機案例

`created` 從 2026-11-02 (週一) 起算 0 到 20 天, 時間以 1, 15, 30 或 60 分鐘為單位. `hours` 有 80% 從常見值挑選 (0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 8, 9, 16, 40), 其餘是 0.25 的倍數. holidays 從 11 月中隨機挑選 0, 1 或 3 天.

---

## booking: 會議室預約

### 需求 (`request.txt`)

> 新增 booking.py,做一個會議室預約簿 class BookingBook,方法: book(room: str, start: int, end: int) 預約, cancel(booking_id: int) 取消, free_slots(room: str, day_start: int, day_end: int) 查詢空檔. 時間用從當天 00:00 起算的分鐘數. 同一間會議室的預約不能重疊. 要附上測試.

### 意圖卡 (`intent.md`)

- book 成功時回傳 int 的預約編號. 和現有預約重疊時回傳 `None`, 不丟例外.
- 時段是半開區間 `[start, end)`: 前後相接不算重疊.
- `start >= end`, `start < 0` 或 `end > 1440`: book 丟 `ValueError`.
- 預約編號從 1 開始, 每次成功預約加 1, 所有會議室共用同一個序號. 失敗的預約不占編號. 取消後的編號不會重複使用.
- cancel 成功時回傳 `True`. 編號不存在或已經取消過時回傳 `False`.
- free_slots 回傳依時間排序的 `list[tuple[int, int]]`. 部分超出查詢範圍的預約要裁切. 長度為 0 的空檔不列出.
- free_slots 查詢沒有預約的會議室: 回傳 `[(day_start, day_end)]`.
- free_slots 的 `day_start >= day_end`: 丟 `ValueError`.
- 會議室名稱區分大小寫.

### 陷阱

| 陷阱 | 常見的錯誤 |
|---|---|
| 前後相接 | 用閉區間, 10:00-11:00 和 11:00-12:00 被判為重疊 |
| 重疊時的回傳值 | 丟例外, 或回傳 `False` |
| 編號規則 | 每間會議室各自編號, 失敗的預約也占編號, 或重複使用取消的編號 |
| 空檔的邊界 | 列出長度為 0 的空檔, 或沒有裁切超出範圍的預約 |

### Hidden test 規則案例

`back-to-back allowed`, `overlap returns None`, `contained overlap None`, `rooms independent`, `room case-sensitive`, `start>=end ValueError`, `start<0 ValueError`, `end>1440 ValueError`, `full day ok`, `ids start at 1 shared`, `failed booking no id`, `ids not reused`, `cancel twice False`, `cancel unknown False`, `cancel frees slot`, `free empty room`, `free sorted gaps`, `free no zero-length`, `free clip`, `free fully booked`, `free after cancel`, `free bad range ValueError`.

### 隨機案例

每組 1 到 25 個操作, 會議室是 A 或 B:

- 55% 是 book: 時間以 30 分鐘為單位, 長度 0 到 120 分鐘. 有 5% 的機率超出範圍或 `end < start`.
- 20% 是 cancel: 編號 0 到 8.
- 25% 是 free_slots: 起點以 60 分鐘為單位, 長度 0 到 600 分鐘, 終點最大到 1440.

意圖卡沒有定義查詢範圍超過 1440 的情況, 所以隨機案例不產生這種輸入. 第一版的生成器產生了這種輸入, 兩版都被誤判失敗. 這個問題已經修正.

---

## tagval: Tag Validator (對照組)

### 需求 (`request.txt`)

> 新增 tag_validator.py,提供 is_valid(code: str) -> bool,檢查一段程式碼片段是否合法,規則和 LeetCode 591 Tag Validator 相同: 整段程式碼必須被一個合法的封閉標籤包住; 標籤名稱只能是 1 到 9 個大寫英文字母; 開始和結束標籤要正確配對巢狀; 標籤內容可以有其他合法封閉標籤, CDATA 區段 (<![CDATA[ ... ]]>,內容原樣保留,不解析) 和一般字元,但不能有不配對的 '<'; 遇到 '<' 或 '</' 時,一直到下一個 '>' 都視為標籤名稱. 要附上測試.

### 意圖卡

完全依照 LeetCode 591 的規則, 沒有其他偏好.

### Hidden test

- 32 個 edge 案例: LeetCode 的範例, 加上 `"a"`, 只有 CDATA, 10 個字母的標籤名稱, `<A></A><B></B>`, `<A></A >` 等. 每次執行時, 都先用這些案例驗證參考實作.
- 隨機案例: 先產生深度最多 4 層的標籤樹, 偶爾使用不合法的名稱. 內容混合子標籤, CDATA 和一般字元. 然後隨機刪除或插入 0 到 2 個字元. 合法和不合法的案例約各占一半.
- 效能: `<A>` 內含 20,000 個 `<B>x</B>`, 時間上限 3 秒.

參考實作在 LeetCode 官方解法的基礎上, 修正了兩個邊界問題: 只有 `"a"` 或只有 CDATA 時, 官方解法會誤判成合法.

---

## pilot 題目 (正式測試不使用)

這 3 題的需求直接寫 "規則和 LeetCode N 相同", 並列出細節. 兩版都能照記憶寫對, 所以只保留作為參考.

| 題目 | 模組 | Hidden test |
|---|---|---|
| justify (LeetCode 68) | `text_justify.full_justify` | 10 個 edge, 3000 個隨機案例, 效能: 200,000 個字, 6 秒 |
| lfu (LeetCode 460) | `lfu_cache.LFUCache` | 4 個 edge, 3000 個隨機操作序列 (以 O(n) 參考實作比對), 效能: 混合 200,000 次操作, 以及 250,000 次連續淘汰, 各 6 秒. O(n) 解在效能案例會超時 |
| regex (LeetCode 10) | `regex_match.is_match` | 17 個 edge, 3000 個隨機案例, 效能: 4 個會讓回溯解爆炸的輸入, 各 2 秒 |

# Olist Portfolio · Excel 說明文件

`output/portfolio.xlsx`(10 visible sheet + 1 hidden = 11 sheets,~85 KB)
是 Olist 巴西電商分析的 Excel-form 版本作品集。本文件說明每一頁在做什麼、
公式怎麼接、為什麼這樣設計。

由 `notebook/build_portfolio_xlsx.py` 自動產出。重新生成:

```bash
python notebook/build_portfolio_xlsx.py
```

build 流程:openpyxl 寫底層 → win32com 後處理(加真 PivotTable + Power Query 連線)。

---

## 設計四大原則

### 1. Single source of truth — `_data_calc`(隱藏)

所有 visible sheet 的數字都從 `_data_calc` 抓。這張 sheet 內含 11 個區塊,
全部包成 Excel Table:

| Table | 用途 |
|---|---|
| `tbl_kpi_lookup` | 16 對(metric, value)— 給 KPI Scale 區塊 |
| `tbl_yearly` | 3 列年度 KPI |
| `tbl_revenue` | 27 列月份營收 |
| `tbl_rfm` | 6 列客群(Customers, Customer %, Revenue, Revenue %, ARPU, Recency)|
| `tbl_installments` | 5 列 bucket(+ Total Revenue / Repeat Customers 兩個分量)|
| `tbl_logistics` | 27 列州 |
| `tbl_cohort` | 27×13 矩陣 |
| `tbl_status_raw` | 5 列 status(從 raw 聚合)|
| `tbl_payment_raw` | 4 列 payment(從 raw 聚合)|
| `tbl_headlines` | 7 個衍生指標(VLOOKUP / XLOOKUP / 算式)|
| `tbl_constants` | 3 個假設值(Default Repeat-spend rate / CRM cost / Custom recall rate)|

改源 CSV → 重跑 build → `_data_calc` 整體重算 → 10 個 dashboard sheet 同步動。

### 2. 公式用 cell ref 當 key + 整欄 ref(資料源透明)

**之前**:`=XLOOKUP("Total orders", _data_calc!$A$3:$A$18, _data_calc!$B$3:$B$18, 0)`
- 寫死字串 `"Total orders"` + 寫死範圍

**現在**:`=XLOOKUP(B7, _data_calc!$A:$A, _data_calc!$B:$B, 0)`
- key 從同列 B 欄 cell 讀(`B7` = "Total orders" label)
- 範圍是整欄 `$A:$A`(看就知道在 _data_calc 工作表 A 欄)
- 換 B7 的 label,C7 結果立刻變

`_xlfn.XLOOKUP(...)` 前綴是 openpyxl 寫 modern Excel function 的必要 prefix
(Excel 顯示時自動省略,顯示為 `=XLOOKUP(...)`)。

### 3. 算式邏輯放在 visible sheet,不藏進 _data_calc

reviewer 點 cell 想看到「這個數字怎麼算的」。算式拆分如下:

| 視圖 sheet | 衍生 metric | 公式 |
|---|---|---|
| 03 KPI Status / Payment | Share | `=C27/SUM($C$27:$C$31)` (這列 ÷ 全部)|
| 03 KPI YoY | GMV YoY | `=C22/C21-1` (本年 ÷ 去年 − 1)|
| 04 Revenue | MoM growth | `=C7/C6-1` |
| 05 RFM | Customer % | `=C6/SUM($C$6:$C$11)` |
| 05 RFM | Revenue % | `=E6/SUM($E$6:$E$11)` |
| 05 RFM | ARPU | `=E6/C6` (revenue ÷ customers,同列)|
| 08 Installments | Avg ticket | `=XLOOKUP(B6, ..., Total Rev) / C6` |
| 08 Installments | Repeat rate | `=XLOOKUP(B6, ..., Repeat Customers) / E6` |
| 09 Logistics | ETA gap | `=D6-C6` (Estimated − Actual)|

`_data_calc` 只存「分子分母」(訂單數、營收、回購數),除法在 visible cell 進行。

### 4. 互動性需求 → 真 PivotTable

`10_Pivot_Analysis` 用真 Excel PivotTable(win32com 後處理建)。reviewer 拖
欄位、加 Slicer、雙擊 drill-down 都會。其他 sheet 是固定 KPI / 圖表 dashboard,
不需要重切視角,所以用 XLOOKUP 算。

---

## Sheet 逐頁說明

### 01_Cover

入口頁:

- **Title block**(B2:E3)— 專案名稱 + 副標
- **3 個 headline 卡**(B11:D13)— 直接 cell ref + cell format(**不是** TEXT 字串):
  - B11: `=_data_calc!$B$137`,format `"R$ "#,##0,"K"` → R$ 469K
  - C11: `=_data_calc!$B$139`,format `0.00%` → 1.81%
  - D11: `=_data_calc!$B$138`,format `0.00"×"` → 3.48×

  formula bar 顯示乾淨 cell ref,顯示字串靠 cell number_format 處理,不用字串 concat。

- **Banner**(row 15)— TEAL 一條,合併 PivotTable 跳轉連結 + Power Query 操作指引
- **SHEETS IN THIS WORKBOOK**(B17+)— 內建 TOC,9 個跳轉連結
- **LIVE LINKS** + **TECH STACK** — 補充資料

TOC 編號(B19:B27)儲存為 int 用 format `"00"` 顯示 → 不會出現「數字儲存為文字」綠角警告。

### 02_Data_Dictionary

Schema 文件 + 9 張 raw sample(各 3 列):

- **Schema overview** — 9 表的 row 數 + 一行說明
- **9 個 sample 區塊** — orders / customers / items / payments / reviews /
  products / sellers / geolocation / category translation
- 每張 sample 用「**variety-based 取樣**」: 抓 3 列「不重複的分類值」(state /
  category / payment_type / review_score),避免 reviewer 看到三列都同一個值

不放完整 raw(1.55M rows 太大)。

### 03_KPI_Dashboard

4 個區塊:

| 區塊 | Cell | Key | 算式邏輯 |
|---|---|---|---|
| Scale & Coverage | C7:C15 | B 欄 metric label | XLOOKUP `=XLOOKUP(B7, _data_calc!$A:$A, _data_calc!$B:$B, 0)` |
| Yearly KPIs | C20:F22 | B 欄年份 | XLOOKUP × 4 metric;**G 欄 GMV YoY** = `C22/C21-1`(2017 因 2016 只 3 個月,顯示 `—`)|
| Order Status | C27:D31 | B 欄 status | XLOOKUP orders + **Share = C27/SUM($C$27:$C$31)** |
| Payment Mix | C36:E39 | B 欄 payment | 同上 |

Status / Payment 不是寫死的,是 build 從 99K orders + 104K payment lines 真實聚合 →
存 `_data_calc!tbl_status_raw` + `tbl_payment_raw` → XLOOKUP 拉。

### 04_Revenue_Trend

月份 × 營收 + MoM 成長:

- **Table**(B5:D32)— 27 個月 × 3 欄(Month / Revenue / MoM growth)
- **Revenue** = XLOOKUP from `_data_calc!tbl_revenue`
- **MoM growth** = `=C7/C6-1`(本月 ÷ 上月 − 1)
  - 2017-01: `—`(沒有上月)
  - 2018-10: `—`(資料截至月中,truncated → 顯示 -90% 是假象)
- **3-color scale** 紅(衰退)→ 白(持平)→ 綠(成長)
- Line chart 看 Nov 2017 Black Friday peak

### 05_RFM_Segments

6 個客群 RFM(NTILE window function):

- **Table**(B5:I11)— Champions / At Risk / Loyal Low-spend / Average / Potential New / Lost
- 每列只 XLOOKUP **原始量**(Customers / Revenue / Recency),其他都是 visible 公式:
  - Customer % = `=C6/SUM($C$6:$C$11)`
  - Revenue % = `=E6/SUM($E$6:$E$11)`
  - **ARPU = `=E6/C6`**(完全不用 _data_calc,直接看右邊 revenue 除左邊 customers)
- Conditional formatting:Customer % 資料條(綠)、Revenue % 資料條(橘)、ARPU 三色紅綠燈
- Pareto chart

### 06_Cohort_Heatmap

13 個月留存矩陣(cohort × M0~M12):

- **2D 查找** — `=INDEX(matrix, MATCH(cohort_month, keys, 0), MATCH(month_label, headers, 0))`
- **Color scale**(白→黃→橘)— M1 那欄 0.2-0.7%(深橘)
- 為什麼 INDEX/MATCH 而非 XLOOKUP:**二維**,需要 row + col 同時定位

### 07_ROI_Calculator

互動式 At-Risk win-back ROI 試算器,**4 個輸入全部公式**:

| Cell | 來源 |
|---|---|
| C7 At-Risk count | `=XLOOKUP("At Risk", _data_calc!$A:$A, _data_calc!$B:$B, 0)` |
| C8 ARPU | `=XLOOKUP("At Risk", _data_calc!$A:$A, _data_calc!$F:$F, 0)` |
| C9 Repeat-spend rate | `=XLOOKUP("Default Repeat-spend rate", ...)` from Constants |
| C10 CRM cost | `=XLOOKUP("Default CRM cost (R$)", ...)` from Constants |

reviewer type 數字會覆寫公式(實際使用 UX)。

- **Named Ranges**:`At_Risk_Count` / `ARPU` / `Repeat_Spend` / `CRM_Cost`
  → scenario 公式可讀:`=At_Risk_Count*C15*ARPU*Repeat_Spend`
- **4 個 scenarios**:Conservative 5% / Optimistic 10% / Aggressive 20% /
  **Custom**(F 欄黃色,F15 預設值 = `=XLOOKUP("Default Custom recall rate", ...)`,可 type 覆寫)

### 08_Installments

巴西分期付款 → ARPU + 留存:

- **Table**(B5:F10)— 5 個 bucket
- 公式:
  - Orders = `XLOOKUP(B6, _data_calc!$A:$A, _data_calc!$B:$B, 0)`
  - **Avg ticket = `XLOOKUP(...Total Rev) / C6`**(division 看得見)
  - Customers = XLOOKUP
  - **Repeat rate = `XLOOKUP(...Repeat Customers) / E6`**(division 看得見)
- 條件格式:Avg ticket 資料條,Repeat rate 三色圖示
- 兩張 bar chart

### 09_Logistics

27 州 ETA(承諾)vs Actual(實際):

- **Table**(B5:E32)— 27 列
- Actual / Estimated = XLOOKUP from `_data_calc`
- **ETA gap = `=D6-C6`**(visible 減法,完全不依賴 _data_calc)
- 條件格式:ETA gap 三色比例尺、Actual / Estimated 資料條
- Bar chart: SP 8.8d(最快)vs RN 19.3d(最慢)

### 10_Pivot_Analysis

**唯一一個用真 Excel PivotTable 的 sheet。**

- **PivotTable**(B5)— State(Rows) × Payment type(Columns) × Total Orders
- Tabular layout + 強制英文 label(`pt.DataFields(1).Caption = "Total Orders "` /
  `pt.GrandTotalName = "Grand Total"` / `pt.RowAxisLayout(2)` 替換掉「列標籤 / 欄標籤 / 加總 - Orders / 總計」)
- reviewer 可:
  - 拖欄位重排視角
  - 右鍵 Insert Slicer
  - 雙擊任一格 drill-down
  - Refresh All 從 source 重算
- **Source: `tbl_payments_long`**(I5:K128)— 從 99K orders + 96K customers
  + 104K payments 真實聚合的長表

### _data_calc(隱藏)

中央資料倉,11 張 Excel Table。reviewer 想看可以右鍵 sheet tab → 取消隱藏。

---

## 業界 Excel 範式對照

| 範式 | 本檔案怎麼做 |
|---|---|
| **三層架構** Raw → Calc → Output | `_data_calc`(Calc)→ 10 visible(Output)。Raw 在 GitHub repo |
| **數字前綴 sheet 命名** | `01_Cover` / `02_Data_Dictionary` / … 順序穩定 |
| **Excel Tables(ListObject)** | 30+ 張 table,所有表格區塊 Ctrl+T |
| **Named Ranges** | 4 個(ROI 輸入)|
| **禁用 merged cells 做表頭** | 用 Center Across Selection 取代,共 0 merged cells |
| **Frozen panes** | 9 個 sheet 有 |
| **Conditional Formatting** | 14 個區塊(資料條 / 三色比例尺 / 圖示集 / color scale)|
| **Live formula linking** | 800+ formulas,KPI 卡全部 XLOOKUP / INDEX-MATCH |
| **真 PivotTable** | 10_Pivot_Analysis(win32com 後處理建)|
| **真 live query** | qry_orders_live(Power Query Web → GitHub raw,Refresh All 重抓)|
| **No emoji** | 全部換成 conditional formatting icon set |

---

## Power Query live connection(POC)

`qry_orders_live` 已透過 win32com 寫進 xlsx,M code:

```
let
    Source = Csv.Document(Web.Contents(
        "https://raw.githubusercontent.com/kengkeng44/olist-project/master/data/olist_orders_dataset.csv"
    ), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers
```

**Reviewer 怎麼用**:
1. 開 xlsx → Data 索引標籤 → **Queries & Connections** 窗格
2. 看到 `qry_orders_live`(Connection only)
3. 右鍵 → **Load To...** → Table → 選 sheet → OK
4. Excel HTTP GET https://raw.githubusercontent.com/.../olist_orders_dataset.csv → 99K rows 落表
5. 之後改 GitHub 上的 CSV → **Refresh All** → 重抓

**為什麼不在 build 時自動 Load**:Excel Trust Center 對 Web 連接器需要使用者首次同意,
COM 自動化無法越過(`E_INVALIDARG`)。POC 採「query 已註冊,reviewer 一鍵載入」的折衷。

**已知限制**:
- GitHub raw 對匿名請求 60 次/小時 rate limit
- `order_items.csv` 110 MB 接近 raw timeout 邊界
- 正式 portfolio 應遷移到 OneDrive / SharePoint(Microsoft 官方推薦)

---

## 升級到 Power Pivot Data Model(senior signal)

openpyxl 能寫 Tables / Formulas / Conditional Formatting / Named Ranges,
但 Power Pivot 是 Excel UI 內建,程式自動化困難。手動步驟:

1. **Power Query**:Data → Get Data → From Folder → 指 `/data`,每個 CSV 變一個 Query
2. **Power Pivot**:File → Options → Add-ins → Power Pivot。Queries 載入 Data Model,
   建關聯:`orders[customer_id] → customers`、`items[order_id] → orders`、
   `payments[order_id] → orders`
3. **DAX measure**:`Total Revenue := SUMX(items, items[price] + items[freight_value])`
4. **Dashboard 改寫**:把 `_data_calc!Bx` 換成
   `=CUBEVALUE("ThisWorkbookDataModel", "[Measures].[Total Revenue]")`
5. Refresh All 即從 raw 重算整本

完成後可處理百萬 row 等級的 production 資料。

---

## 不合理數字的處理

YoY / MoM 公式遇到 partial baseline 會輸出垃圾數字(+14750%、-90%)。已抑制:

| 位置 | 為什麼抑制 |
|---|---|
| 03 KPI YoY G21(2017)| 2016 Olist 才剛上線(僅 9-12 月有資料),5.94M ÷ 0.04M = +14750% 是假象 |
| 04 Revenue MoM D32(2018-10)| 2018-10 資料截至月中,本月 ÷ 上月 = -90% 是 truncation 不是真實衰退 |

兩處都顯示 `—` 並加 italic caveat 註解。

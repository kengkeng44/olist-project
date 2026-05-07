# Olist Portfolio · Excel 說明文件

`output/portfolio.xlsx`(10 visible sheet + 1 hidden = 11 sheets,~78 KB)
是 Olist 巴西電商分析的 Excel-form 版本作品集。本文件說明每一頁在做什麼、
公式怎麼接、為什麼這樣設計。

由 `notebook/build_portfolio_xlsx.py` 自動產出。重新生成:

```bash
python notebook/build_portfolio_xlsx.py
```

---

## 設計三大原則

### 1. Single source of truth — `_data_calc`(隱藏)

所有 visible sheet 的數字都從一張隱藏 sheet `_data_calc` 抓。這張 sheet 內含
8 個區塊(KPI lookup / Yearly KPIs / Monthly Revenue / RFM / Installments /
Logistics / Cohort matrix / Order Status / Payment mix / Derived Headlines),
每個區塊都包成 Excel Table(`tbl_kpi_lookup`、`tbl_rfm`…)。

改源 CSV → 重跑 build script → `_data_calc` 重算 → 10 個 dashboard sheet
全部跟著動。手寫資料 0 處(除 ROI 假設)。

### 2. 公式用名稱當 key,不靠 row 順序

主要查找用 **XLOOKUP**(Excel 2021/365)keyed by 業務名稱:

```
=XLOOKUP("At Risk", _data_calc!$A$54:$A$59, _data_calc!$B$54:$B$59, 0)
                ↑ key                                                ↑ default
```

語意自帶:看到 `XLOOKUP("At Risk", ...)` 就知道在抓 At-Risk 客群數。
若 `_data_calc` 插入新 row,公式仍然對(因為查的是名稱而非位置)。

`_xlfn.XLOOKUP(...)` 前綴是 openpyxl 寫 modern Excel function 的必要 prefix
(Excel 顯示時自動省略,顯示為 `=XLOOKUP(...)`)。

### 3. 互動性需求 → 真 PivotTable

`10_Pivot_Analysis` 是唯一用真 Excel PivotTable 的 sheet。reviewer 可以拖
欄位、加 Slicer、雙擊 drill-down。其他 sheet 是固定的 KPI / 圖表式 dashboard,
不需要重切視角,所以用 XLOOKUP 算。

---

## Sheet 逐頁說明

### 01_Cover

入口頁。三大區塊:

- **Title block**(B2:E3)— 專案名稱 + 副標
- **3 個 headline 卡**(B11:D13)— 全部公式驅動:
  - B11: `="R$ "&TEXT(_data_calc!$B$137/1000,"0")&"K"` → R$ 469K
  - C11: `=TEXT(_data_calc!$B$139,"0.00%")` → 1.81%
  - D11: `=TEXT(_data_calc!$B$138,"0.00")&"×"` → 3.48×
- **SHEETS IN THIS WORKBOOK**(B16+)— 內建 TOC,9 個跳轉連結
- **LIVE LINKS** — Streamlit / GitHub Pages / Tableau / Repo / PDF
- **TECH STACK** — 7 個工具 chips

**不用 sheet 02 做 TOC** 是因為只放 Cover 一頁就把入口資訊全給齊。

### 02_Data_Dictionary

Schema 文件 + 真 raw sample。

- **9 source tables**(B6:D15)— 每張表的 row 數 + 一行說明
- **5 個 sample 區塊**(orders / customers / items / payments / reviews
  各 3 row from raw CSV)— 讓 reviewer 看真實資料樣貌

不放完整 raw(1.55M rows 太大)。要看完整資料 → GitHub repo `/data` 目錄。

### 03_KPI_Dashboard

整個專案的數字總覽,4 個區塊全 XLOOKUP:

| 區塊 | Cell | Key |
|---|---|---|
| Scale & Coverage | C7:C15 | metric 名稱(`Total orders` 等)|
| Yearly KPIs | C20:F22 | 年份(2016/2017/2018)|
| Order Status mix | C27:D31 | status 名稱(`delivered` 等)|
| Payment Mix | C36:E39 | payment_type(`credit_card` 等)|

Status / Payment 不是寫死的,是 build script 從 99K orders + 104K payment
lines 真實聚合 → 存進 `_data_calc` → XLOOKUP 拉。

### 04_Revenue_Trend

月份 × 營收的趨勢分析。

- **Table**(B5:C32)— 27 個月,每行 `=XLOOKUP(B6, months, revenue, 0)`
- **Line chart** — 看 Nov 2017 Black Friday peak

### 05_RFM_Segments

6 個客群的 RFM 分析(NTILE window function 切的)。

- **Table**(B5:I11)— Champions / At Risk / Loyal / Average / Potential / Lost
  共 6 列,每列 6 個 metric 都 XLOOKUP 用 segment 名稱當 key
- **條件格式**:Customer % 資料條(綠)、Revenue % 資料條(橘)、ARPU 三色紅綠燈
- **Pareto chart** — Customer share vs Revenue share 對比

### 06_Cohort_Heatmap

13 個月的留存矩陣(cohort × M0~M12)。

- **2D 查找** — `=INDEX(matrix, MATCH(cohort_month, keys, 0), MATCH(month_label, headers, 0))`
- **Color scale**(白→黃→橘)— M1 那欄全部是 0.2-0.7%(深橘),視覺證明 retention 失敗
- 為什麼用 INDEX/MATCH 不用 XLOOKUP:**二維查找**,需要 row + col 同時定位

### 07_ROI_Calculator

互動式 At-Risk win-back ROI 試算器。

- **Inputs**(C7:C10)— 4 個輸入:
  - **C7**(At-Risk count)= XLOOKUP from RFM(資料驅動的預設值,可手動覆寫)
  - **C8**(ARPU)= XLOOKUP from RFM
  - **C9**(Repeat-spend rate)= 0.5(模型假設,非資料)
  - **C10**(CRM cost)= 50,000(預算假設)
- **Named Ranges**:`At_Risk_Count` / `ARPU` / `Repeat_Spend` / `CRM_Cost`
  → 公式可讀:`=At_Risk_Count*C15*ARPU*Repeat_Spend`
- **4 個 scenarios**(C-F: Conservative 5% / Optimistic 10% / Aggressive 20%
  / Custom 10%)
- **Recall rate**(列 15)是 scenario 定義 — 改它整欄重算
- **Custom 欄(F)**是黃色可編輯,reviewer 可以輸入自己想試的 recall rate

### 08_Installments

巴西分期付款文化 → ARPU + 留存的影響。

- **Table**(B5:F10)— 5 個 bucket(1 / 2-3 / 4-6 / 7-10 / 11+ installments)
- 每行:`=XLOOKUP(B6, buckets, value_col, 0)` × 4 metrics
- **條件格式**:Avg ticket 資料條,Repeat rate 三色圖示
- **2 張 bar chart** — AOV by bucket、Repeat rate by bucket

### 09_Logistics

27 州的 ETA(承諾)vs Actual(實際)送達天數。

- **Table**(B5:E32)— 27 列 × 3 個 XLOOKUP
- **條件格式**:ETA gap 三色比例尺(綠=平台估準,紅=過度保守)+ Actual / ETA
  資料條
- **Bar chart** — Actual vs Estimated 對比,SP 8.8d(最快)vs RN 19.3d(最慢)

### 10_Pivot_Analysis

**唯一一個用真 Excel PivotTable 的 sheet。**

- **PivotTable**(B5)— State(Rows) × Payment type(Columns) × Sum of Orders
  - reviewer 可拖欄位重排
  - 右鍵 → Insert Slicer 加切片器
  - 雙擊任一格 drill-down 看明細
  - Refresh All 從 source 重算
- **Source: `tbl_payments_long`**(I5:K128)— 從 99K orders + 96K customers
  + 104K payments 真實聚合的長表(state, payment_type, orders 三欄)

為什麼這頁用 PivotTable 不用 XLOOKUP:**互動需求** — PM 場景下「我想換維度看」
是真實使用情境(原本看 state,想換成 看 payment;或加入 month 做 trend)。
靜態 XLOOKUP 表做不到。

### _data_calc(隱藏)

中央資料倉。8 個區塊全是 Excel Table:

| Table | 內容 | 給誰用 |
|---|---|---|
| `tbl_kpi_lookup` | 16 對(metric, value)| KPI Dashboard Scale 區塊 |
| `tbl_yearly` | 3 列年度 KPI | KPI YoY 區塊 |
| `tbl_revenue` | 27 列月份營收 | Revenue Trend |
| `tbl_rfm` | 6 列客群 | RFM Segments + ROI Calc(C7/C8)|
| `tbl_installments` | 5 列 bucket | Installments |
| `tbl_logistics` | 27 列州 | Logistics |
| `tbl_cohort` | 27×13 矩陣 | Cohort Heatmap |
| `tbl_status_raw` | 5 列 status(從 raw 聚合)| KPI Status |
| `tbl_payment_raw` | 4 列 payment(從 raw 聚合)| KPI Payment |
| `tbl_headlines` | 7 個衍生指標(VLOOKUP / XLOOKUP / 算式)| Cover 3 卡 |

---

## 業界 Excel 範式對照

| 範式 | 本檔案怎麼做 |
|---|---|
| **三層架構** Raw → Calc → Output | `_data_calc`(Calc)→ 10 visible sheets(Output)。Raw 留在 GitHub repo |
| **數字前綴 sheet 命名** | `01_Cover` / `02_Data_Dictionary` / … 順序穩定 |
| **Excel Tables(ListObject)** | 27 張 table,所有表格區塊 Ctrl+T |
| **Named Ranges** | 4 個(ROI 輸入)|
| **禁用 merged cells 做表頭** | 用 Center Across Selection 取代,共 0 merged cells |
| **Frozen panes** | 9 個 sheet 有(reviewer 滾動不會迷路)|
| **Conditional Formatting** | 10 個區塊(資料條 / 三色比例尺 / 圖示集)|
| **Live formula linking** | 745+ formulas,KPI 卡全部 XLOOKUP / INDEX-MATCH |
| **真 PivotTable** | 10_Pivot_Analysis(win32com 後處理建)|
| **No emoji** | 全部換成 conditional formatting icon set |

---

## 已內建一個 Power Query live connection(POC)

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
2. 看到 `qry_orders_live` 是 connection-only 查詢
3. 右鍵 → **Load To...** → Table → 選 sheet → OK
4. Excel 會 HTTP GET https://raw.githubusercontent.com/.../olist_orders_dataset.csv,99K rows 直接落表
5. 之後改了 GitHub 上的 source CSV → 點 **Refresh All** → 重抓

**為什麼不在 build 時自動 Load 到 sheet**:Excel 隱私 / Trust Center 對 Web 連接器需要使用者首次同意,COM 自動化無法越過此 prompt(`E_INVALIDARG`)。POC 採「query 已註冊,reviewer 一鍵載入」的折衷。

**已知限制**:
- GitHub raw 對匿名請求 60 次/小時 rate limit,大量 reviewer 同時用會踩到 429
- `order_items.csv` 110 MB 接近 raw.githubusercontent.com timeout 邊界
- 正式 portfolio 應遷移到 OneDrive / SharePoint 共用連結(Microsoft 官方推薦)

---

## 升級到 Power Query / Power Pivot(senior signal)

openpyxl 能寫 Tables / Formulas / Conditional Formatting / Named Ranges,
但 Power Query 和 Power Pivot 是 Excel UI 內建,程式自動化困難。手動步驟:

1. **Power Query**:Data → Get Data → From Folder → 指 `/data`,每個 CSV
   變一個 Query
2. **Power Pivot**:File → Options → Add-ins → Power Pivot。把 Queries 載入
   Data Model,建關聯:`orders[customer_id] → customers`、
   `items[order_id] → orders`、`payments[order_id] → orders`
3. **DAX measure**:`Total Revenue := SUMX(items, items[price] + items[freight_value])`
4. **Dashboard 改寫**:把 `_data_calc!Bx` 換成
   `=CUBEVALUE("ThisWorkbookDataModel", "[Measures].[Total Revenue]")`,
   Refresh All 即從 raw 重算整本

完成後可以處理百萬 row 等級的真實 production 資料。

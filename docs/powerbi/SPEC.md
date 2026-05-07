# Olist · Power BI Edition — Spec

## 定位

把現有的 olist-project 分析（已有 Python notebook + Tableau public dashboard）以 Power BI 重製,作為 PM portfolio 的第三個載體。

**差異化重點**:Power BI 版加入互動式 ROI Simulator(What-If parameter),把 R$ 469K 召回機會從靜態洞察升級為可決策工具 — 這是 Tableau 版做不到的。

履歷一句話:「將同一份巴西電商分析以 Power BI 重製,加入互動式 ROI 模擬器,讓主管可即時拉動召回率參數試算 9.4× ROI 區間。」

---

## 範圍 — 3 頁(從 6 頁壓縮)

| # | 頁面 | 重點 visual | 工時 |
|---|---|---|---|
| 1 | Executive Summary | KPI cards、月營收趨勢、巴西州地圖、Top 3 品類 | 3h |
| 2 | RFM + Cohort | 6 區段堆疊條、Cohort matrix、1.81% repeat rate banner | 4h |
| 3 | **ROI Simulator**(亮點頁) | What-If recall rate slider、動態 ROI KPI、3 情境對照 | 3h |
| - | 資料載入 + 星型模型 + Calendar 表 | 一次做好 | 2h |

**總計 ~12 小時**(週末兩天可收工)。

砍掉的頁面:Logistics 獨立頁、Installment 獨立頁、Payment Insights 細節頁。理由:這些洞察可放回 Page 1 KPI/註解,獨立成頁邊際效益低。

---

## 5 天執行計畫

### Day 1(3h)— 資料 + 模型
- 安裝 Power BI Desktop(免費)
- Power Query 載入 9 張 CSV(`/data/*.csv`)
- 建立星型模型關聯,**用 `customer_unique_id` 不要 `customer_id`**
- 建 Calendar 表(DAX 一段抄)
- 過濾 `order_status = 'delivered'`(97% 主分析用)

### Day 2(3h)— Page 1 Executive Summary
- 4 個 KPI cards:Total Revenue、Total Customers、AOV、Repeat Rate
- 月營收 line chart(2017-Q4 高峰標註)
- 巴西州 map(SP/RJ/MG/RS/PR = 77% 訂單)
- Top 3 品類 donut(Health & Beauty / Watches & Gifts / Bed Bath Table)
- **2018-09 後資料不完整 → 全頁 time-series 加灰色註記**

### Day 3(4h)— Page 2 RFM + Cohort
- 左半:6 segment 堆疊條(客戶數 vs 營收佔比)
  - Champions 16.2% / 31.4%、At-Risk 23.5% / 35.5%
  - banner: "39.7% 客戶創造 66.9% 營收 — Pareto"
- 右半:Cohort retention matrix(列=首購月、欄=月 0–12)
  - 條件式格式色階
  - banner: "1.81% repeat rate — acquisition-driven platform"

### Day 4(3h)— Page 3 ROI Simulator(履歷亮點)
- What-If parameter:`Recall Rate` 0–30%, step 1%
- 動態 measure: `Projected Revenue = [At-Risk Count] * [Recall Rate] * 213 * 0.5 - 50000`
- 3 情境對照表(Conservative 5% / Baseline 10% / Aggressive 20%)
- 大號 KPI 卡:即時 ROI 倍數、預估回收金額
- 結論文字:"At-Risk 21,975 人、ARPU R$ 213、固定成本 R$ 50K 假設"

### Day 5(2h)— 收尾
- 統一配色(對齊 README / Tableau 版色系)
- 截圖 3 頁 → 放 `docs/powerbi/screenshots/`
- 更新 README 加 Power BI 章節 + 連結
- Push branch + PR

---

## 必學 DAX measures(8 個)

```
Total Revenue       = SUM(payments[payment_value])
Total Customers     = DISTINCTCOUNT(orders[customer_unique_id])
AOV                 = DIVIDE([Total Revenue], DISTINCTCOUNT(orders[order_id]))
Repeat Rate         = CALCULATE + FILTER(>1 單客戶 / 總客戶)
Recency Days        = DATEDIFF(MAX(purchase_date), TODAY(), DAY)
RFM Score           = RANKX 三次後 SWITCH 分組(NTILE 等價)
Revenue YoY %       = SAMEPERIODLASTYEAR
Projected ROI       = What-If parameter 串動態計算
```

第 6 個(RFM)最難,Copilot 或 Claude 直接生。

---

## AI 工具組合

| 工具 | 用途 | 費用 |
|---|---|---|
| **Power BI Desktop** | 主要開發環境 | **免費** |
| Power BI Copilot(PPU) | 自動生報告/DAX/敘事 | $20/月,**60 天試用** |
| Claude / ChatGPT | 寫 DAX、debug | 既有訂閱 |
| Mokkup.ai | 進 Power BI 前的版面 wireframe | 免費 |
| DAX Studio | 測 measures | 免費 |

**建議組合**:Power BI Desktop(免費)+ Claude 寫 DAX。如果有時間開 PPU 60 天試用,做完就退訂。

---

## 關鍵資料品質注意事項(來自原 README)

1. 用 `customer_unique_id` 不要 `customer_id`(後者有 3,345 筆重複)
2. 主分析過濾 `order_status = 'delivered'`(97%)
3. 2018-09 後資料不完整 — time-series 標記
4. Credit card 73.9% / boleto 19% / voucher 5.6% / debit 1.5%

---

## 關鍵商業數字(KPI 直接抄)

- 99,441 訂單、96,096 unique 客戶
- 國家平均到貨 15.4 天 vs ETA 24 天(快 36%)
- SP 8.8 天 vs RN 19.3 天(2.2× 落差)
- 7–10 期分期 = 一次付清 ARPU 的 3.48×、回購率高 65%
- At-Risk 21,975 人、ARPU R$ 213、393+ 天未活躍
- Aggressive 召回 20% × R$ 213 × 50% 回流 - R$ 50K = **R$ 469K 機會、9.4× ROI**

---

## 交付物 checklist

- [ ] `olist-powerbi.pbix`(放 `tableau/` 同層,新建 `powerbi/` 資料夾)
- [ ] 3 頁截圖(`docs/powerbi/screenshots/page1-3.png`)
- [ ] README 加 Power BI 章節(連 .pbix 下載 + 截圖)
- [ ] PR merge 回 master

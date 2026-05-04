# Olist Project — TODO

README v2 已完成 portfolio 等級改寫:EDA 概況、ER 圖、ROI 試算、規則式 vs K-Means 取捨、Tableau 嵌入、How to reproduce 全部到位。剩下待辦聚焦在「進階分析深化」。

---

## ✅ 已完成

- [x] **#1 EDA 資料概況段** — notebook §3 + README 第三章(99,441 訂單、73.9% credit_card、SP 41.9%、月營收 2018-09 紅虛線標註)
- [x] **#2 9 張表的 Schema / ER 圖** — README 第四章 Mermaid ER 圖,標註 `customer_id` vs `customer_unique_id`
- [x] **#3 Insight 量化 ROI** — README 第八章三情境 (5%/10%/20% 召回率 → ROI 2.3×/4.7×/9.4×)
- [x] **#5 K-Means vs 規則式分群取捨** — README 第十章三點論述
- [x] **#7 Tableau dashboard 連結 + 截圖** — README 已嵌入
- [x] **#8 How to reproduce** — README 「如何執行」章節

---

## 🟡 進行中 / 下一步

- [ ] **#4 Cohort / Retention 月留存熱力圖** — X 軸購買後 N 個月、Y 軸 cohort 月份。視覺化「F=1.0 全平台單次客」這個 README 第七章的核心發現。最高優先級。
- [ ] **#6 巴西分期付款洞察** — 用 `order_payments.payment_installments` 挖:8 期以上 ARPU vs 一次付清差幾倍?分期數 vs 退貨率?差異化王牌,台灣履歷少撞題。
- [ ] **#9 LICENSE 檔** — 30 秒的事:repo 根目錄加 `LICENSE` 貼 CC-BY-NC-SA-4.0 全文(目前只在 README 引用,沒實檔)。

---

## 🔵 進階(Phase 2,1 個月內)

- [ ] **商品評分 vs 物流天數相關檢定** — Pearson / Spearman 相關 + 散點圖,把「物流爛 → 1 星」量化驗證
- [ ] **Tableau dashboard 升級** — 加入 RFM 分群互動篩選器,從傳統 BI 報表升級成探索式 dashboard

---

## ⚪ 評估後決定不做

- ~~評論情緒分析 NLP~~ — 葡萄牙文 NLP 工具鏈麻煩,PM 履歷 CP 值低
- ~~機器學習滿意度預測~~ — PM 面試不太會問,技術深度給其他專案展現
- ~~Silhouette / Davies-Bouldin 分群品質指標~~ — 過度技術,PM 用不到

---

## 🚀 戰略選擇(Phase 3,下個月決定)

這個專案做到此已足夠當 PM portfolio 主打,接下來二選一:
- **走深**:挑「ROI 召回」做完整 A/B 測試模擬 + 假設驗證,變成可執行的 PM 提案文件
- **走廣**:開新專案,做「行為事件分析」(SaaS 漏斗 / Funnel) 補 portfolio 廣度。電商分析 + SaaS 行為分析在 PM 履歷少撞題。

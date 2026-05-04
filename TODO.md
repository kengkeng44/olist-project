# Olist Project — TODO

README v3 完成 12 章節 portfolio 級分析:EDA、ER 圖、RFM、Cohort 留存、ROI 試算、巴西分期付款洞察全部到位 + LICENSE。Phase 1 全部結束。

---

## ✅ 已完成

- [x] **#1 EDA 資料概況段** — notebook §3 + README 第三章(99,441 訂單、73.9% credit_card、SP 41.9%、月營收 2018-09 紅虛線標註)
- [x] **#2 9 張表的 Schema / ER 圖** — README 第四章 Mermaid ER 圖,標註 `customer_id` vs `customer_unique_id`
- [x] **#3 Insight 量化 ROI** — README 第九章三情境 (5%/10%/20% 召回率 → ROI 2.3×/4.7×/9.4×)
- [x] **#4 Cohort 留存熱力圖** — README 第八章 + `notebook/cohort_analysis.py`(93,358 客戶,僅 1.81% 跨月回購;M1 留存 0.2-0.7%)
- [x] **#5 K-Means vs 規則式分群取捨** — README 第十二章三點論述
- [x] **#6 巴西分期付款洞察** — README 第十章 + `notebook/installments_analysis.py`(7-10 期 ARPU R$334 = 一次付清的 3.48×;回購率 4.13% = 65% 提升)
- [x] **#7 Tableau dashboard 連結 + 截圖** — README 已嵌入
- [x] **#8 How to reproduce** — README 「如何執行」章節
- [x] **#9 LICENSE 檔** — repo 根目錄 CC-BY-NC-SA-4.0 全文(438 行)

---

## 🟡 進階(Phase 2,1 個月內)

- [ ] **PPT / Slides 簡報** — 把 README 12 章濃縮成 10-12 頁面試簡報(Marp markdown 可直接生 PPT/PDF)
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

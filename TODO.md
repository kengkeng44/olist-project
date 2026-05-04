# Olist Project — TODO

README 第一版已完成 RFM 分群 + 4 條 insight。比對 Kaggle 高讚 Notebook 後，列出待補項目。

---

## 🔴 必補（影響 README 第一印象，PM portfolio 標配）

- [x] **#1 EDA 資料概況段** — 已加入 notebook §3（規模快照 + 訂單狀態 / 付款 / 州別三大分布），README 第三章節同步寫入實際數字（99,441 訂單、73.9% credit_card、SP 佔 41.9%）。月營收圖已加 2018-09 紅色虛線標註。
- [x] **#2 9 張表的 Schema / ER 圖** — README 第四章節加入 Mermaid ER 圖，標註 `customer_id` vs `customer_unique_id` 差異說明。
- [x] **#3 Insight 量化成 ROI** — README 第八章節三情境試算（5% / 10% / 20% 召回率對應 ROI 2.3× / 4.7× / 9.4×）。

---

## 🟡 加分（拉開頂尖 vs 中段距離）

- [ ] **#4 Cohort / Retention 月留存熱力圖** — X 軸購買後 N 個月、Y 軸 cohort 月份。預期會看到第一個月後幾乎全黑，視覺化「F=1.0 全平台單次客」這個結論。
- [ ] **#5 K-Means vs 規則式分群的取捨說明** — 不需真的跑 K-Means，但要在 README 寫清楚為什麼選規則式（業務可解釋性、F 鑑別力低、可移植）。
- [ ] **#6 巴西分期付款洞察** — 用 `order_payments.payment_installments` 挖：分 8 期以上 ARPU vs 一次付清 ARPU 差異。這是 Olist 資料的獨家賣點，台灣履歷少撞題。

---

## 🔵 v2 / 後續（Tableau dashboard 完成後）

- [ ] **#7 Tableau Public dashboard 連結 + 截圖嵌入 README**
- [ ] **#8 README 加 "How to reproduce" 區塊** — Python 版本、套件版本、執行步驟（從 clone 到產出 output/）
- [ ] **#9 加 LICENSE 與 CC-BY-NC-SA-4.0 引用聲明**（Kaggle 來源規定）

---

## ⚪ 評估後決定不做（避免之後又重新評估）

- ~~評論情緒分析 NLP~~ — 葡萄牙文 NLP 工具鏈麻煩，PM 履歷 CP 值低
- ~~機器學習滿意度預測~~ — PM 面試不太會問，技術深度給其他專案展現
- ~~Silhouette / Davies-Bouldin 分群品質指標~~ — 過度技術，PM 用不到

---

## 執行順序建議

下一步：**#1 EDA 概況段**（1–2 小時，影響最大）→ #2 Schema → #3 ROI → 收尾後再看 #4–#6

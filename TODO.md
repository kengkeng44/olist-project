# Olist Project — TODO

README 第一版已完成 RFM 分群 + 4 條 insight。比對 Kaggle 高讚 Notebook 後，列出待補項目。

---

## 🔴 必補（影響 README 第一印象，PM portfolio 標配）

- [ ] **#1 EDA 資料概況段** — 訂單數 / 客戶數 / 賣家數 / 類目數 / 時間跨度 / 州別 / 訂單狀態分布。放月營收趨勢圖 + 州別熱力圖 + 付款方式長條圖三件組。註解 2018/09 後的營收斷崖（資料截斷，非真實衰退）。
- [ ] **#2 9 張表的 Schema / ER 圖** — 用 Mermaid 畫關聯圖，說明 `customer_id` vs `customer_unique_id` 的差異（同一個人在不同訂單會有不同 customer_id）。
- [ ] **#3 Insight 量化成 ROI** — 召回流失風險群的試算：召回率 5% / 10% 各帶來多少營收，假設 EDM 成本，算 ROI 倍數。PM 履歷必備，不能空泛說「應該召回」。

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

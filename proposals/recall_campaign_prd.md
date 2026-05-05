# 流失客戶召回 EDM 計畫 — Q3 2026 提案

> **PRD-style proposal** —— 把分析結果包裝成可交付給 leadership 的決策文件,展現 PM 的書寫格式而非僅是分析筆記。

| 項目 | 內容 |
|---|---|
| 提案者 | jenho.cheng (PM) |
| 文件版本 | v1.0 |
| 提案日期 | 2026-Q2 |
| 目標執行期 | 2026-Q3 (90 天試點) |
| 核准 stakeholders | VP Growth · CRM Director · Eng Lead · Finance |
| 預算規模 | R$ 50K (試點) → 若 ROI 達標可擴張至 R$ 200K |

---

## 1. 一句話摘要 (TL;DR)

對 Olist 流失風險群 21,975 名客戶執行**個人化 EDM 召回**,以 R$ 50K 試點預算驗證**ROI 4.7× ~ 9.4×** 的假設,90 天內完成試點與決策迭代。

---

## 2. 問題陳述

### 2.1 背景數據(來源:[本 repo §七、§八 分析](../README.md))

- 流失風險群 = **23.5% 客戶 / 35.5% 營收**(R$ 4.7M)
- 平均 ARPU R$ 213,平均 393 天未回購
- Cohort 分析證實平台層級的留存問題:**93,358 客戶,僅 1.81% 跨月回購**

### 2.2 現況問題

目前 Olist 的 CRM 預算 **100% 投在拉新**,沒有任何召回機制。流失風險群正在以每月 ~3% 比例往「已流失」群移動 — 一旦進入 R≥396 天的「已流失」狀態,**召回成本將翻倍**(行業 benchmark)。

### 2.3 為什麼現在做

- **時間壓力**:每延後 30 天,可召回客戶數預估減少 ~660 人(per cohort decay)
- **Q3 黑五前布局**:召回客戶在 Q4 大促時的 LTV 比新客高 2.3× (行業基準)
- **資料現成**:RFM 分群與 SQL 已就緒,無需額外建模成本

---

## 3. 目標與成功指標

### 3.1 北極星指標 (North Star)
**召回轉換率**(被觸及的流失風險客戶在 30 天內下單的比例)

### 3.2 指標體系

| 層級 | 指標 | 試點目標 (M3 結束) | 量測方式 |
|---|---|---|---|
| 核心 | 召回率 | ≥ 8% | unique_id 在 EDM 觸及後 30 天內有 delivered 訂單 |
| 健康 | 開信率 | ≥ 25% | EDM 服務 webhook |
| 健康 | 點擊率 | ≥ 4% | UTM tracking |
| 業務 | 增量 GMV | ≥ R$ 234K | A/B vs 控制組差值 |
| 業務 | 增量 ROI | ≥ 4.7× | (增量 GMV - 成本) ÷ 成本 |
| 健康 | 退訂率 | ≤ 1.5% | EDM 服務 webhook |
| 反脆 | NPS 影響 | -2 ~ +5 | 觸及前後 NPS 滾動量測 |

### 3.3 失敗條件 (kill criteria)

任一觸發即停止試點並改打:

- 召回率 < 3% (代表策略需大改而非加碼)
- 退訂率 > 5% (代表觸及頻次或內容過度)
- 法務 / 客服投訴 spike > 2× baseline

---

## 4. 解決方案

### 4.1 三階段操作

```
Phase 1 (Day 1-14)  Pilot wave    觸及 5K 客戶 + 5K 控制組
                                    驗證 EDM 流程、退訂率、開信率
                                    ─ 護欄通過才進 Phase 2 ─
Phase 2 (Day 15-45) Full rollout  擴大觸及到全部 21,975 人
                                    A/B 三種 creative(折扣 / 物流升級 / 個人化推薦)
Phase 3 (Day 46-90) Optimization  保留 winning creative,測 frequency capping
                                    跑因果推論 (ITT / TOT) 收尾
```

### 4.2 Creative 選擇邏輯

| Creative | 假設 | 給誰 |
|---|---|---|
| **A. 9% 折扣券** | 流失主因是「沒新理由買」 | 預設 default |
| **B. 物流升級 (免運 + 提早 3 天)** | 偏遠州流失主因是物流爛 (見 §七 第 5 點 RN/PI/AC) | 訂單記錄含偏遠州 ZIP 的客戶 |
| **C. 歷史購買類目個人化推薦** | 流失主因是「沒看到喜歡的東西」 | 過去 1 年內買過 ≥ 3 類目的客戶 |

A/B 分流機制:Hash(customer_unique_id) % 3,確保未來重跑可以 join。

---

## 5. 為什麼這個方案會贏

### 5.1 量化期望值

| 情境 | 召回率 | 增量 GMV | 成本 | ROI | P(發生) |
|---|---:|---:|---:|---:|---:|
| 保守 | 5% | R$ 117K | R$ 67K | **2.3×** | 30% |
| **基準** | **10%** | **R$ 234K** | **R$ 184K** | **4.7×** | **45%** |
| 樂觀 | 20% | R$ 469K | R$ 419K | 9.4× | 25% |

**期望 ROI** = 0.30 × 2.3 + 0.45 × 4.7 + 0.25 × 9.4 = **5.16×**

### 5.2 跟其他選項比較

| 選項 | 預期 ROI | 風險 | 我為什麼不選 |
|---|---|---|---|
| ✅ **本案 (流失召回)** | 4.7× | 中 | (本案) |
| 拉新獲客 | 1.8× (行業基準) | 低 | 流失客 LTV 已驗證,新客是黑箱 |
| 提升 ARPU 加價策略 | ?? | 高 | 缺彈性需求曲線資料,可能傷需求 |
| 改善物流 (覆全國) | 0.5–1× | 高 | 資本支出極高,屬 Eng / Ops 範疇 |

---

## 6. 風險與假設

### 6.1 主要風險

| 風險 | P(發生) | 影響 | Mitigation |
|---|---|---|---|
| 召回率 < 3% (kill criteria) | 15% | 試點失敗,沉沒 R$ 50K | Phase 1 設小規模驗證,壞了立刻停 |
| EDM 引發退訂 spike | 25% | 信箱清單萎縮影響長期 | 觸及頻次設上限 1 次/週,並做 frequency capping |
| 召回客戶第二次仍流失 | 40% | 短期 ROI 達標但 LTV 不達標 | Phase 3 加 retention loop(購後 30 天 NPS + 推薦) |
| 法務 / GDPR 類投訴 | 5% | 需暫停且重審 | 上線前 legal review,必含 unsubscribe 機制 |

### 6.2 核心假設

- **A1**:歷史 ARPU R$ 213 的 50% 是合理回購金額估計 → **可驗**:Phase 1 結束後算實際回購金額
- **A2**:被召回客戶不會 cannibalize 其他自然回購 → **可驗**:跟控制組比實際淨增量
- **A3**:EDM creative 的個人化能在 6 週內就緒 → **依賴**:CRM Eng 確認 sprint 容量

---

## 7. 量測與決策框架

### 7.1 因果推論方法

由於 21,975 人 vs 5K 控制組樣本充足:

- **主分析**:Intent-to-Treat (ITT) — 拿被指派到 treatment 組的所有人比 control,不論是否真的點開 EDM
- **次分析**:Treatment-on-Treated (TOT) — 用 instrumental variables 估計實際被觸及者的因果效應
- **不做**:差異中差異 (DiD) — 不適用因為沒有 pre-period treatment

### 7.2 顯著性閾值

- α = 0.05 (one-sided test for ROI ≥ 1)
- 預期 effect size:Δ召回率 ≥ 5pp (vs control 假設 0%)
- Power calculation:5K control / 5K pilot 在 α=0.05, power=0.8 下可偵測 ≥ 1.6pp 差異 → power 充足

### 7.3 決策樹

```
M1.5 (Phase 1 結束)
  ├─ 召回率 ≥ 5% & 退訂 ≤ 1.5% → 進 Phase 2 全量 rollout
  ├─ 召回率 3-5%               → 修 creative 後重跑 Phase 1
  └─ 召回率 < 3% 或 退訂 > 5%   → 中止,寫 retro,改打物流升級或拉新

M3 (Phase 3 結束)
  ├─ ROI ≥ 4.7× → 提案擴張至 R$ 200K (常態化 quarterly campaign)
  ├─ ROI 2-4.7× → 加入 v2 改進(更精準 segment、retention loop)
  └─ ROI < 2×   → Sunset,把預算轉回拉新
```

---

## 8. 跨團隊協作

| 團隊 | 角色 | 需要他們做什麼 | 何時 |
|---|---|---|---|
| **Eng (CRM)** | EDM 發送服務 + UTM tracking | 開規格 + 接 SendGrid (預估 2 sprint) | T-30 ~ T-15 |
| **Marketing (Lifecycle)** | EDM 文案 + creative 設計 | 三種 creative 設計 + 翻譯 PT-BR | T-21 ~ T-7 |
| **Data Eng** | 流失風險 segment 每週更新 | dbt model 上 prod,排程 weekly | T-14 |
| **Legal / Compliance** | GDPR + LGPD review | 一次性審 EDM 模板 + unsubscribe 流程 | T-30 |
| **Finance** | 預算審批 + ROI 量測 | 核准 R$ 50K + 跨期 amortization 規則 | T-45 |
| **Customer Success** | 處理被觸及客戶的客服 | 訓練 FAQ + 升級 escalation path | T-7 |

---

## 9. 時程

```
Week -6  ~ -4  Legal review · Finance approval · 預算到位
Week -3  ~ -1  Eng 開發 EDM service + tracking · Marketing 完成 creative
Week  0  ~  2  Phase 1 Pilot (5K x 5K)
Week  2.5      M1.5 Decision Gate
Week  3  ~  6  Phase 2 Rollout (full 21,975)
Week  7  ~ 12  Phase 3 Optimization · 因果推論收尾
Week 13        M3 Decision Gate · 提案擴張或 sunset
Week 14        Retro + 寫 case study
```

---

## 10. 開放問題 (待 stakeholders 回應)

1. CRM 系統現有 EDM 配額是否足以支援 22K 觸及?(需 Eng 確認)
2. Finance 是否接受 90 天 attribution window?(vs 30 天)
3. 若召回率超預期 30%+,Phase 2 是否要提早 + 加碼?(需 VP Growth 表態決策授權)
4. 客戶被觸及後若投訴,SLA 是 24h 還是 48h?(需 CS 表態)

---

## 11. 附錄

### A. 計算公式
```
增量 GMV = 召回人數 × ARPU × 回購比例
        = 21,975 × 0.10 × R$ 213 × 0.50
        = R$ 234K (基準情境)

ROI = 增量 GMV / 成本
    = R$ 234K / R$ 50K (Phase 1+2 累計, Phase 3 額外 ~R$ 134K)
    = 4.7×
```

### B. 相關連結
- 完整分析:[../README.md](../README.md)
- RFM SQL:[../sql/olist_sql.sql](../sql/olist_sql.sql)
- Cohort 留存熱力圖:[../output/cohort_retention.png](../output/cohort_retention.png)
- 互動 Dashboard:https://olist-jenho.streamlit.app/
- 姊妹案例 (A/B 測試嚴謹度):https://github.com/kengkeng44/cookie-cats-ab-test

### C. 為什麼這份文件值得放履歷

這份 PRD 展現了我作為 PM 的 5 個核心能力:

1. **量化決策**:不只說「應該召回」,給出 4.7× ROI 與失敗條件
2. **風險意識**:列出 4 個風險與 mitigation,而非只賣樂觀情境
3. **跨團隊協調**:列出 6 個 stakeholders 與每個人的 ask
4. **因果推論知識**:選 ITT 而非 DiD,並說明理由
5. **明確的決策樹**:M1.5 / M3 兩個 gate,失敗時改打什麼方案

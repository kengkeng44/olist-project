# Cowork Brief — Hex Setup Phase

> 給 Claude Cowork 的單一任務指令。Cowork 做完報告完成,使用者再接手核心分析 cells。

---

## 任務目標

在 hex.tech 建立一個新 project,載入 Olist 分析資料,**不要做任何分析或建圖** — 只做環境設定。

完成後輸出兩個東西給使用者:
1. **Project URL**(類似 `https://app.hex.tech/<workspace-id>/hex/<project-id>/draft/logic`)
2. **第一個 Python cell 的執行結果**(列出 dataframe 的 shape)

---

## 步驟

### Step 1 — 確認 Hex 帳號
1. 打開 https://hex.tech
2. 若未登入:點 Sign up,用 Google 帳號 `jenho.cheng@gmail.com` 登入
3. 若已登入:跳到 Step 2

### Step 2 — 建 workspace(若已有跳過)
1. 進到 home → 若沒有 workspace,點 Create workspace
2. Workspace name:`kengkeng44-portfolio`
3. Plan:選 **Community**(免費)

### Step 3 — 建 project
1. 點右上 **+ New project**
2. Type:**Python project**
3. Name:`Olist RFM Analysis`
4. Description:`Brazilian e-commerce customer segmentation with R$469K reactivation opportunity`

### Step 4 — 加第一個 Python cell(載入資料)
1. 進到 project,canvas 上加一個 **Python cell**
2. 貼以下程式碼:

```python
import pandas as pd

BASE = "https://raw.githubusercontent.com/kengkeng44/olist-project/master/output"

rfm = pd.read_csv(f"{BASE}/rfm_segments.csv", encoding="utf-8-sig")
revenue = pd.read_csv(f"{BASE}/revenue.csv", encoding="utf-8-sig")
revenue["月份"] = pd.to_datetime(revenue["月份"])
state = pd.read_csv(f"{BASE}/state.csv", encoding="utf-8-sig")
kpi = pd.read_csv(f"{BASE}/kpi_yearly.csv", encoding="utf-8-sig")
cohort = pd.read_csv(f"{BASE}/cohort_retention.csv", encoding="utf-8-sig", index_col=0)
category = pd.read_csv(f"{BASE}/category.csv", encoding="utf-8-sig")
installments = pd.read_csv(f"{BASE}/installments.csv", encoding="utf-8-sig")

print("Data loaded successfully:")
print(f"  RFM segments: {rfm.shape}")
print(f"  Revenue months: {revenue.shape}")
print(f"  States: {state.shape}")
print(f"  KPI yearly: {kpi.shape}")
print(f"  Cohort matrix: {cohort.shape}")
print(f"  Top categories: {category.shape}")
print(f"  Installments buckets: {installments.shape}")
```

3. **Run the cell** (Shift+Enter 或點 Run)

### Step 5 — 驗證 + 回報
1. 確認 cell 沒有錯誤
2. 截圖或複製 cell 輸出文字
3. 從瀏覽器網址列複製 project URL

---

## 完成後輸出格式

請以這個格式回報給使用者:

```
✅ Hex setup complete

Project URL: <貼網址>

Cell 1 output:
<貼第一個 cell 的 print 輸出>

Ready for next step (核心分析 cells).
```

---

## ⛔ 不要做的事

- 不要建任何 chart cell
- 不要做 treemap / heatmap / KPI single-value cell
- 不要排版 / 進 App Builder
- 不要 publish

這些是使用者要親手做的部分(學習目的)。

---

## 出錯時怎麼辦

| 錯誤 | 處理 |
|---|---|
| Hex 註冊需要驗證信 | 暫停,告訴使用者:「請去 email 點驗證連結後告訴我」 |
| Pandas import 失敗 | 檢查 Hex project 是否選了正確 Python kernel(`Python 3.10+`) |
| GitHub raw URL 404 | 確認網址正確,試 `curl https://raw.githubusercontent.com/kengkeng44/olist-project/master/output/rfm_segments.csv` 看 GitHub 是否 reachable |
| Workspace 已存在 | 直接用現有的,不要重複建 |

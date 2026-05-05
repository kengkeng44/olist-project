# Olist on Hex — Build Spec

> 把 Olist 分析在 Hex 重做一份,展示「modern data stack」能力。預估 2-3 小時。

---

## 為什麼做 Hex 版本

| 工具 | 業界訊號 | 你已做 |
|---|---|---|
| Streamlit | Python web app,適合 SaaS / startup | ✅ |
| Tableau Public | 傳統大企業 BI keyword | ⏳ spec 在 tableau/ |
| HTML + Plotly | 自由度高,GitHub Pages 免費 | ✅ |
| **Hex** | **modern data team(SaaS / 新創)首選, 2024-2026 熱詞** | ⬜ 本 spec |

Hex 的差異化在於「**SQL + Python + 互動 input + 共享連結 一頁解決**」 — 跟 Streamlit 比少了部署環節,跟 Jupyter 比多了互動跟共享。

---

## 註冊 + 設定

1. https://hex.tech → Sign up(用 Google 帳號)
2. 進首頁 → 新建 workspace,命名 `kengkeng44-portfolio`
3. Settings → Plan = **Community** (免費,可發 public link)
4. Project → New Project → 命名 `Olist RFM Analysis`

---

## 資料連線(任選一)

### 選項 A:直接拉 GitHub raw CSV(最快)

Hex 的 SQL cell 不直接吃 CSV,但 Python cell 可以:

```python
import pandas as pd
BASE = "https://raw.githubusercontent.com/kengkeng44/olist-project/master/output"
rfm = pd.read_csv(f"{BASE}/rfm_segments.csv", encoding="utf-8-sig")
revenue = pd.read_csv(f"{BASE}/revenue.csv", encoding="utf-8-sig")
state = pd.read_csv(f"{BASE}/state.csv", encoding="utf-8-sig")
cohort = pd.read_csv(f"{BASE}/cohort_retention.csv", encoding="utf-8-sig", index_col=0)
```

### 選項 B:接 BigQuery (展示企業級 stack,加分大)

1. Google Cloud → 新建 project `olist-portfolio`
2. BigQuery → Create dataset → upload `output/*.csv`
3. Hex → Data sources → Add → BigQuery → 用 service account JSON 認證
4. SQL cell 可以直接寫:`SELECT * FROM olist.rfm_segments`

> **推薦選項 B 給履歷加分**(會 BigQuery 是 modern data engineer 必備),但選項 A 5 分鐘可以開始。

---

## Project 結構(7 個 cells)

| # | Type | 內容 |
|---|---|---|
| 1 | **Markdown** | Hero — 標題、TL;DR、headline metrics |
| 2 | **SQL / Python** | 載入資料 |
| 3 | **Markdown** + **Metric** | 4 個 KPI cards (Total GMV / Orders / AOV / Rating) |
| 4 | **Chart** | 月營收趨勢線圖 + 2018-09 標註 |
| 5 | **Input + Chart** | 互動 RFM treemap(下拉選 segment 看細節) |
| 6 | **Chart** | Cohort 留存熱力圖 |
| 7 | **Markdown** | 結論 + ROI 試算 + 連結 |

---

## Cell 1 — Hero (Markdown cell)

```markdown
# 🇧🇷 Olist 巴西電商分析

> 從 99,441 筆交易找出 **R$ 469K 召回機會 (ROI 9.4×)** 與 **平台級留存問題**

**作者**:jenho.cheng  ·  **資料來源**:[Olist Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
**完整 GitHub**:[kengkeng44/olist-project](https://github.com/kengkeng44/olist-project)
**姊妹作**:[Cookie Cats A/B 測試](https://github.com/kengkeng44/cookie-cats-ab-test)

---

## TL;DR
- RFM 分群顯示 **23.5% 客戶 (流失風險群) 貢獻 35.5% 營收** → 召回 ROI 4.7-9.4×
- Cohort 分析證實平台層級的留存問題 (M1 留存 0.2-0.7%,基準 5-15%)
- 巴西分期付款是 **隱形 CRM** (7-10 期 ARPU 是一次付清的 3.48×)
```

---

## Cell 2 — Load data (Python cell)

```python
import pandas as pd
BASE = "https://raw.githubusercontent.com/kengkeng44/olist-project/master/output"

rfm = pd.read_csv(f"{BASE}/rfm_segments.csv", encoding="utf-8-sig")
revenue = pd.read_csv(f"{BASE}/revenue.csv", encoding="utf-8-sig")
revenue["月份"] = pd.to_datetime(revenue["月份"])
state = pd.read_csv(f"{BASE}/state.csv", encoding="utf-8-sig")
kpi = pd.read_csv(f"{BASE}/kpi_yearly.csv", encoding="utf-8-sig")
cohort = pd.read_csv(f"{BASE}/cohort_retention.csv", encoding="utf-8-sig", index_col=0)

print(f"RFM segments: {len(rfm)}, Revenue months: {len(revenue)}, States: {len(state)}")
```

---

## Cell 3 — KPI cards (4 個 Single Value cells)

Hex 內建 **Single Value** cell type,直接拖到 canvas 上:

| Cell | Value 來源 (Python expression) | Format |
|---|---|---|
| Total GMV | `f"R$ {kpi['總營收_M'].sum():.1f}M"` | Text |
| Total Orders | `int(kpi['總訂單數'].sum())` | Number with thousands separator |
| AOV | `f"R$ {kpi['總營收_M'].sum()*1e6/kpi['總訂單數'].sum():.0f}"` | Text |
| Avg Rating | `f"{(kpi['平均評分']*kpi['總訂單數']).sum()/kpi['總訂單數'].sum():.2f} ★"` | Text |

排版用 Hex 的 layout grid → 4 個 Single Value cells 並排。

---

## Cell 4 — 月營收線圖 (Chart cell)

Chart cell 設定:
- **Data source**:`revenue` dataframe
- **Chart type**:Line
- **X**:`月份`
- **Y**:`總營收`
- **Color**:固定 `#1a1a2e`
- **Reference line**:在 `2018-09-01` 加紅色虛線,label「資料截斷」

如果 Hex 的 chart 不支援 reference line,改用 Plotly cell:

```python
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=revenue["月份"], y=revenue["總營收"],
                          mode="lines+markers", line=dict(color="#1a1a2e", width=3)))
fig.add_vline(x=pd.Timestamp("2018-09-01").timestamp()*1000,
              line_dash="dash", line_color="#e63946",
              annotation_text="2018-09 資料截斷")
fig.update_layout(title="月營收趨勢 2017–2018", height=400)
fig
```

---

## Cell 5 — 互動 RFM Treemap (Input + Chart) ⭐

這個是 Hex 最能 show off 的地方 — 加 input widget。

### 5a. Input cell

- Type:**Dropdown**
- Label:「篩選分群」
- Options:`["全部"] + rfm["segment"].tolist()`
- Variable name:`selected_segment`
- Default:「全部」

### 5b. Python cell(用 input 篩資料)

```python
if selected_segment == "全部":
    df = rfm
else:
    df = rfm[rfm["segment"] == selected_segment]
df
```

### 5c. Chart cell(treemap)

- Data:上一個 cell 輸出
- Type:**Treemap**
- Path:`segment`
- Values:`營收佔比_%`
- Color:`平均_M_元` (ARPU)
- Color scale:`#fee5d9` → `#a50f15`

---

## Cell 6 — Cohort 留存熱力圖 (Plotly cell)

```python
import plotly.graph_objects as go
import numpy as np

z = cohort.values
text = np.where(np.isnan(z), "",
                np.where(z >= 99, "100%",
                         np.where(z < 0.05, "0", np.round(z, 1).astype(str))))

fig = go.Figure(data=go.Heatmap(
    z=z, x=cohort.columns, y=cohort.index,
    colorscale=[[0, "#fffafa"], [0.05, "#fee5d9"], [0.2, "#fcae91"],
                [0.5, "#fb6a4a"], [1, "#a50f15"]],
    zmin=0, zmax=5,
    text=text, texttemplate="%{text}",
    colorbar=dict(title="回購率 %"),
))
fig.update_layout(
    title="Cohort 留存熱力圖 — F=1.0 鐵證",
    xaxis_title="購買後第 N 個月",
    yaxis=dict(title="Cohort 月份", autorange="reversed"),
    height=600,
)
fig
```

---

## Cell 7 — 結論 (Markdown)

```markdown
## 🎯 PM 決策

**召回 ROI 試算**

| 情境 | 召回率 | 增量營收 | ROI |
|---|---:|---:|---:|
| 保守 | 5%  | R$ 117K | **2.3×** |
| 基準 | 10% | R$ 234K | **4.7×** |
| 樂觀 | 20% | R$ 469K | **9.4×** |

**完整 PRD**:[recall_campaign_prd.md](https://github.com/kengkeng44/olist-project/blob/master/proposals/recall_campaign_prd.md)

---

## 我做了什麼

- SQL Window Function (NTILE) 規則式分群,而非 K-Means
- Cohort 留存佐證「平台級單次客」現象
- 量化召回機會為 R$ 469K (ROI 9.4×)
- 寫 PRD-style 提案文件展示 PM 書寫格式

> 想看更多互動?
> - [Streamlit 完整版](https://olist-jenho.streamlit.app/)
> - [GitHub repo](https://github.com/kengkeng44/olist-project)
```

---

## App Builder(把 cells 排成 dashboard view)

Hex 有 **App Builder**(類似 Streamlit 的 layout),把 cells 拖成 dashboard 給非技術用戶看:

1. 點 Project 右上 **App** tab
2. 拖 Hero markdown 到頂
3. 4 個 KPI cells 排成一橫排
4. 月營收線圖佔全寬
5. 互動 input + Treemap 在左,Cohort heatmap 在右
6. 結論 markdown 收尾

---

## Publish + 分享

1. 右上 **Publish** → toggle "Public"
2. 拿到 URL:`https://app.hex.tech/<workspace>/app/<id>/latest`
3. 加進 Olist README + GitHub profile
4. 履歷掛 keyword:`Hex · Modern Data Stack · BigQuery · SQL`

---

## 完成檢查清單

- [ ] Hex 帳號註冊 + Community plan
- [ ] 資料載入(選 GitHub raw 或 BigQuery)
- [ ] 4 個 KPI single value cells
- [ ] 月營收線圖 + 2018-09 標註
- [ ] 互動 RFM treemap (dropdown filter)
- [ ] Cohort 熱力圖
- [ ] Markdown 結論 + 連結
- [ ] App Builder 排版
- [ ] Publish public 拿 URL

---

## 為什麼這份 spec 值得?

寫完整個 Hex project 後,你的 portfolio 會有 **5 種 dashboard 工具**:
- Streamlit (Python web app)
- HTML + Plotly (static, GitHub Pages)
- Tableau Public (拖拉 BI,委外或自做)
- **Hex** (modern data team 標配)
- 舊版 Tableau

履歷可以掛:**「Streamlit · Hex · Plotly · Tableau」** 一字排開,任何 PM JD 都能對應到至少一個。

---

## 給未來自己的提醒

Hex 的核心賣點不是「另一個 BI 工具」,而是「**SQL + Python + 互動 + 分享 一頁解決**」。展示時要強調這個 — 而不是把它當成「Streamlit 的拖拉版」介紹。

完成後在 README 加段:
> "Why Hex over Streamlit? Streamlit needs Python deployment,Hex 開了 link 就能改參數,適合 internal tool / case study sharing。"

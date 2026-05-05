# Olist Dashboard — Tableau Public Build Spec

> 完整重做規格。設計目標:**1 頁 dashboard、極簡風、3 個圖、4 個 KPI cards**。
> 拿給 freelance designer 做、餵給 AI plugin 問細節、或自己照著建都可以。

---

## 設計原則(必讀)

1. **少即是多**:1 個 dashboard、3 個圖。不要 dashboard 套 dashboard、不要 8 種圖表。
2. **不用花俏色票**:配色限定下方 4 色,不要彩虹。
3. **無動畫無轉場**:Tableau 預設動畫關閉。
4. **手機友善**:設計成 16:9,容器用 Tiled 而非 Floating。
5. **每個圖都要有「So What」**:tooltip + 圖表標題就要說出 insight,不要讓觀眾自己解讀。

---

## 配色與字型

### 色票 (4 色,夠了)

| 用途 | Hex | RGB |
|---|---|---|
| 主色 (深海軍藍) | `#1a1a2e` | (26, 26, 46) |
| 強調紅 (Olist 品牌色) | `#e63946` | (230, 57, 70) |
| 中性灰 (次要文字) | `#94a3b8` | (148, 163, 184) |
| 背景白 / 卡片底 | `#ffffff` / `#f8fafc` | (255, 255, 255) / (248, 250, 252) |

> KPI 數字用主色、變化箭頭/重點用紅、輔助文字用灰。**不要用其他顏色**。

### 字型

- 全部用 Tableau 內建 **Tableau Sans**(跨平台不會亂碼)
- 標題:Tableau Sans Bold 18px
- 內文:Tableau Sans Regular 11px
- 數字:Tableau Sans Bold,KPI 28px、表格 12px

---

## 資料來源(repo 內 CSV,直接連)

從 GitHub raw URL 連線(Tableau Public 支援):

```
https://raw.githubusercontent.com/kengkeng44/olist-project/master/output/<filename>.csv
```

| Sheet 用途 | CSV | 欄位 |
|---|---|---|
| KPI cards | `kpi_yearly.csv` | 年份, 總營收_M, 總訂單數, 平均評分, 平均送達天數 |
| 月營收線圖 | `revenue.csv` | 月份, 總營收 |
| 各州營收 | `state.csv` | 州, 總營收 |
| RFM treemap | `rfm_segments.csv` | segment, 客戶數, 平均_R_天, 平均_F_次, 平均_M_元, 群組總營收, 營收佔比_%, 客戶佔比_% |
| 物流(備用) | `logistics.csv` | 州, 實際天數, 預期天數 |
| 評分分布(備用) | `reviews.csv` | 評分, 數量 |

> 連好之後 → Sheet 1, 2, 3, 4 各自的 Data source 切換對應 CSV。

---

## Sheet 1 — KPI Cards (4 個並排)

**版型**:橫排 4 個,每個是獨立 Sheet 還是用「Container 切 4 等分」都可以。

### Card 1 — 總營收

- **數字**:R$ 13.6M
- 計算公式 (Calculated Field):`SUM([總營收_M])`
- 顯示格式:`R$ 0.0M`
- **副標**:2016–2018 累計 GMV
- 字色:主色 `#1a1a2e`

### Card 2 — 總訂單數

- **數字**:99,441
- 計算公式:`SUM([總訂單數])`
- 顯示格式:`#,##0`
- **副標**:跨 27 州、4,119 城市

### Card 3 — 平均客單

- **數字**:R$ 137
- 計算公式:`SUM([總營收_M]) * 1000000 / SUM([總訂單數])`
- 顯示格式:`R$ #`
- **副標**:每筆訂單平均金額

### Card 4 — 客戶滿意度

- **數字**:4.09 ★
- 計算公式:`SUM([平均評分] * [總訂單數]) / SUM([總訂單數])`
- 顯示格式:`0.00 "★"`
- **副標**:加權平均(2017–2018)
- **顏色條件**:>= 4.0 用 Olist 紅 `#e63946`,< 4.0 用灰

---

## Sheet 2 — 月營收趨勢線圖

**圖類**:Line Chart(線圖)+ 區域填色

### 編碼 (Marks)

- **Columns**:`MONTH([月份])` — 連續日期
- **Rows**:`SUM([總營收])`
- **Mark type**:Line
- 線色:主色 `#1a1a2e`,粗 3pt
- 線下填色:同色 8% 透明度
- 資料點(每月)用紅色 `#e63946`,圓點 size 6

### 註解 (Annotation)

在 **2018-09-01** 加一條垂直紅色虛線(Reference Line):
- 線色:`#e63946`,虛線
- 標註文字(右上):`2018-09 後資料截斷,非真實衰退`

### 標題 & 副標

- 標題:**月營收趨勢 2017–2018**
- 副標:2017 Q4 (黑五+聖誕) 達高峰 R$ 1M;2018 進入穩定期 0.7–1.0M

### Tooltip 客製

```
<MONTH([月份])>
營收:R$ <SUM([總營收])>
```

### 軸格式

- X 軸:每月一個 tick,標籤 `YYYY-MM`,旋轉 0°
- Y 軸:`R$ 0.0M`,網格線淡灰
- 雙軸隱藏

---

## Sheet 3 — 各州營收 (兩個版本擇一)

### 版本 A:Brazil Choropleth Map (推薦,視覺強)

Tableau 內建 Brazil 地圖。需要把 `state.csv` 的 `州`(SP, RJ, MG...) 對應到 Tableau 的 `State/Province`。

- 在 Data Source pane → 右鍵「州」→ Geographic Role → State/Province → Edit Locations → Country: Brazil
- **Marks type**:Map
- **Color**:`SUM([總營收])` → 漸層 `#fee5d9` (淺) → `#a50f15` (深),調整為 sequential 而非 diverging
- **Filter**:勾選 27 個州全部
- Tooltip:`<州>:R$ <SUM([總營收])>` 並加排名 `INDEX()` 計算
- **標題**:各州營收分布 — SP 一州佔 41.9%
- **註解**:在 SP (聖保羅州) 上 hover annotation 「Top 1 — R$ 5.07M (37.3%)」

### 版本 B:Horizontal Bar Top 15 (簡單版)

如果地圖太麻煩,改 bar:

- Columns:`SUM([總營收])`,Rows:`[州]`(用 `RANK_DENSE` 排序取 Top 15)
- Color:Top 5 紅 `#e63946`,其餘灰 `#94a3b8`
- 排序:由大到小
- 加數字 label:`R$ <SUM([總營收])>`

---

## Sheet 4 — RFM Treemap

**圖類**:Treemap(矩形樹狀圖)

### 編碼 (Marks)

- **Mark type**:Square
- **Size**:`SUM([營收佔比_%])` — 面積 = 營收佔比
- **Color**:`SUM([平均_M_元])` (ARPU) — 漸層 `#fee5d9` → `#a50f15`
- **Detail**:`[segment]`
- **Label**:多行
  ```
  <segment>
  營收 <SUM([營收佔比_%])>%
  客戶 <SUM([客戶佔比_%])>%
  ```
- Label 字色:面積大的(冠軍/流失)用白,小的用黑

### Tooltip

```
<segment>
─────────
客戶數:<SUM([客戶數])>
營收佔比:<SUM([營收佔比_%])>%
ARPU:R$ <SUM([平均_M_元])>
平均近度:<SUM([平均_R_天])> 天
```

### 標題 & 副標

- 標題:**RFM 6 分群 — 冠軍 + 流失風險佔 67% 營收**
- 副標:面積 = 營收佔比、顏色深度 = ARPU。流失風險群 (R$ 213, 393 天未回) 是召回 ROI 9.4× 的主要機會

---

## Dashboard 拼版

**畫布尺寸**:1280 × 800 (Tableau 「Custom size」)

**布局** (Tiled 容器,不要 Floating):

```
┌─────────────────────────────────────────────────────────┐
│  Title: Olist 巴西電商分析 · 99,441 筆訂單 · R$ 13.6M GMV │  60px
│  Subtitle: 2016–2018 · 巴西 27 州 · 9 表交叉分析           │
├──────────┬──────────┬──────────┬──────────┐              │
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4   │              │  120px
├──────────┴──────────┴──────────┴──────────┤              │
│                                                          │
│       Sheet 2 — 月營收趨勢線圖 (全寬)                       │  280px
│                                                          │
├─────────────────────────────┬───────────────────────────┤
│                             │                           │
│  Sheet 3 — 各州營收地圖       │  Sheet 4 — RFM Treemap     │  300px
│                             │                           │
└─────────────────────────────┴───────────────────────────┘
                                                  Footer:    40px
                          github.com/kengkeng44/olist-project
```

### 容器設定

- 外層 Vertical Container,Padding 20px、背景 `#ffffff`
- KPI 那排:Horizontal Container,KPI 之間間距 12px
- KPI card 內:背景 `#f8fafc`、圓角 8px(Tableau 不直接支援圓角,用形狀模擬或忽略)
- 兩個下方圖之間:Horizontal Container,間距 16px

---

## 互動 (Filter Actions)

**僅一個 filter 互動**:點 Sheet 3 (州) 會 filter Sheet 2 (月營收) 跟 Sheet 4 (RFM)。

設定:Dashboard → Actions → Add Action → Filter
- Source: Sheet 3 (州地圖)
- Targets: Sheet 2, Sheet 4
- Run on: Select
- Clearing the selection will: Show all values

> **不要做超過這一個互動**,過多互動會讓 dashboard 變混亂。

---

## 標題、註解、Footer

### Dashboard 標題

```
Olist 巴西電商分析
99,441 筆訂單 · R$ 13.6M GMV · 2016–2018
```
字型:Tableau Sans Bold 24px、色 `#1a1a2e`

### Footer

```
資料來源:Brazilian E-Commerce Public Dataset by Olist (Kaggle, CC-BY-NC-SA 4.0)
作者:jenho.cheng · github.com/kengkeng44/olist-project
```
字型:Tableau Sans 9px、色 `#94a3b8`、置中

---

## 發布到 Tableau Public

1. File → Save to Tableau Public As...
2. 命名:`Olist Brazilian E-Commerce Analytics`
3. 描述:把上面的 Dashboard 標題貼進去
4. Tag:`ecommerce`, `RFM`, `customer-segmentation`, `Brazil`, `portfolio`
5. **取消勾選**「Show sheets as tabs」(只顯示 dashboard,不要露出 worksheet)
6. 拿到 URL → 更新 GitHub README 的 Tableau 連結

---

## 反向清單(不要做的事)

- ❌ 不要加圓餅圖(分布類用 bar 或 treemap 即可)
- ❌ 不要用 Tableau 預設的彩虹漸層(看起來廉價)
- ❌ 不要堆超過 3 個 sheet 在 dashboard 上
- ❌ 不要用粗框線、陰影、3D 效果
- ❌ 不要加 logo / 圖示 / 表情符號(Tableau Public 上看起來總是怪怪的)
- ❌ 不要做 dashboard navigation(下拉選單跳頁)— 1 頁就 1 頁
- ❌ 不要顯示 Tableau Public 預設的「View Data」按鈕(關掉)

---

## 完成檢查清單

- [ ] 4 個 KPI cards 都顯示正確數字 (R$ 13.6M / 99,441 / R$ 137 / 4.09 ★)
- [ ] 月營收線圖有 2018-09 紅虛線標註
- [ ] 各州地圖 SP 是最深色
- [ ] RFM treemap 冠軍 + 流失風險明顯佔大塊
- [ ] 點州地圖會 filter 其他兩個圖
- [ ] 配色嚴格只有 4 色
- [ ] 字型統一 Tableau Sans
- [ ] Footer 有 GitHub repo 連結
- [ ] Tableau Public 上看「Show sheets as tabs」是關的
- [ ] Mobile 預覽看起來不擠

---

## 給 AI 工具的 prompt 範本

如果要餵給 ChatGPT / Gemini 問細節,可以用:

> 我要在 Tableau Public 重做一個 dashboard,這是完整 spec(貼整份 md)。請告訴我以下幾件事:
> 1. 把 `state.csv` 的中文「州」欄位映射成 Tableau Brazil 地理角色的步驟
> 2. KPI 4 (加權平均評分) 的 Tableau LOD 公式應該怎麼寫
> 3. Treemap label 的多行格式如何在 Tableau 設定
> 4. 如何隱藏 Tableau Public 預設的「View Data」按鈕

AI 工具可以幫你回答 1-4,但**整個 dashboard 的拼版仍然要你親自進 Tableau 拖拉**。

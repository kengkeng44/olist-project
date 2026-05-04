# Slides

13 頁 PM 面試簡報,把 README 12 章濃縮成可口語講述的版本。

## 編譯成 PPT / PDF

需要先裝 [Marp CLI](https://github.com/marp-team/marp-cli)(node.js 工具):

```powershell
npm install -g @marp-team/marp-cli
```

然後在 repo 根目錄執行:

```powershell
# PDF (推薦,跨平台)
marp slides/portfolio.md -o slides/portfolio.pdf --allow-local-files

# PowerPoint (.pptx)
marp slides/portfolio.md -o slides/portfolio.pptx --allow-local-files

# 開瀏覽器即時預覽 (邊改邊看)
marp slides/portfolio.md -p --allow-local-files
```

> `--allow-local-files` 是必要的,因為簡報引用 `../output/*.png`。

## 結構

| 頁 | 主題 |
|---|---|
| 1 | 封面 — headline metric (R$ 469K) |
| 2 | 為什麼選 Olist(差異化定位) |
| 3 | 資料概況 — 規模 & 巴西特色 |
| 4 | 9 張表 ER 圖 |
| 5 | 分析架構(10 個分析) |
| 6 | 發現 1: RFM 揭露 F=1.0 |
| 7 | 發現 1 佐證: Cohort 熱力圖 |
| 8 | 發現 2: 召回 ROI 試算 |
| 9 | 發現 3: 巴西分期 = 隱形 CRM |
| 10 | 發現 3 行動建議 |
| 11 | 限制與下一步 |
| 12 | 我的差異化 vs Kaggle 多數 Notebook |
| 13 | Q&A |

## 講述時間建議

- 標準版 15 分鐘:每頁 ~70 秒
- 加長版 25 分鐘:留 10 分鐘 Q&A,前 15 分鐘照講
- 電梯版 5 分鐘:只講 1 (封面) → 6 (RFM) → 8 (ROI) → 13 (Q&A)

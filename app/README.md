# Streamlit Dashboard

**🚀 線上版**:https://olist-jenho.streamlit.app/

互動式 dashboard,把 Olist 分析整理成 5 個分頁。比起靜態 README 或 Tableau Public,適合在面試時展示。

## 本機執行

```powershell
# 1. 安裝依賴(repo 根目錄)
pip install -r requirements.txt

# 2. 執行
streamlit run app/Home.py
```

預設開在 http://localhost:8501

## 部署到 Streamlit Cloud(免費)

1. 推 code 到 GitHub(已完成)
2. 進 [share.streamlit.io](https://share.streamlit.io) 用 GitHub 帳號登入
3. 點 **New app** → 選 `kengkeng44/olist-project`
4. **Main file path** 填 `app/Home.py`
5. 點 **Deploy**

約 2 分鐘後拿到一個 `https://olist-xxx.streamlit.app` 的網址。每次 push 到 `master` 自動重新部署。

## 結構

```
app/
├── Home.py              # 入口:headline KPIs + 月營收 + 三大發現連結
└── pages/
    ├── 1_📊_EDA.py      # 規模、訂單狀態、付款結構、評分分布
    ├── 2_🗺️_地理分析.py  # 各州營收 Top 15 + 物流效率對比
    ├── 3_👥_RFM.py      # 6 分群 treemap + 互動 ROI 試算機 ⭐
    ├── 4_📉_Cohort.py   # 互動式留存熱力圖
    └── 5_💳_分期付款.py  # 雙圖比較 ARPU & 回購率
```

## 互動亮點

- **RFM 頁**:ROI 試算機,拖滑桿即時看不同召回率/成本下的 ROI 倍數
- **Cohort 頁**:hover 任一格看精確留存率
- **地理頁**:hover 看每州確切數字
- **所有圖**:點右上角下載 PNG / CSV

## 改動

修改任何 `.py` 後存檔,瀏覽器右上角會跳「Source file changed」按 Rerun 即可。Cloud 端則是 push 後自動重建。

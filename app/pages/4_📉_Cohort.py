"""Cohort 留存熱力圖 — 互動版。"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "output"
PRIMARY = "#1a1a2e"
ACCENT = "#e63946"

st.set_page_config(page_title="Cohort · Olist", page_icon="📉", layout="wide")
st.title("📉 Cohort 留存熱力圖 — F=1.0 的鐵證")
st.caption("驗證「Olist 是獲客驅動而非留存驅動」核心發現")

@st.cache_data
def load(name): return pd.read_csv(OUTPUT / name, encoding="utf-8-sig", index_col=0)

retention = load("cohort_retention.csv")

c1, c2, c3 = st.columns(3)
c1.metric("獨立客戶總數", "93,358")
c2.metric("跨月回購客戶", "1,693", "1.81%")
c3.metric("M1 留存中位數", f"{retention['M1'].median():.2f}%",
          "vs 5-15% 成熟電商基準", delta_color="inverse")

st.divider()

st.subheader("🔥 留存熱力圖")

z = retention.values
text = np.where(np.isnan(z), "",
                np.where(z >= 99, "100%",
                         np.where(z < 0.05, "0", np.round(z, 1).astype(str))))

fig = go.Figure(data=go.Heatmap(
    z=z, x=retention.columns, y=retention.index,
    colorscale=[[0, "#fffafa"], [0.05, "#fee5d9"], [0.2, "#fcae91"],
                [0.5, "#fb6a4a"], [1, "#a50f15"]],
    zmin=0, zmax=5,
    text=text, texttemplate="%{text}",
    textfont={"size": 10},
    colorbar=dict(title="回購率 %", thickness=15),
    hovertemplate="Cohort %{y}<br>%{x}: %{z:.2f}%<extra></extra>",
))
fig.update_layout(
    height=600, margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(title="購買後第 N 個月", side="top"),
    yaxis=dict(title="Cohort 月份(首購月)", autorange="reversed"),
    plot_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🔍 4 個關鍵讀圖")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        f"""
        **1️⃣ M0 全部 100%**
        首購月當然全活躍 — 定義使然。

        **2️⃣ M1 普遍 0.2–0.7%**
        下個月就消失 99% 以上。
        成熟電商 M1 應在 **5–15%**。
        """
    )
with c2:
    st.markdown(
        f"""
        **3️⃣ 整片黃白**
        沒有任何 cohort 在後續月份回升。

        **4️⃣ 1.81% 跨月回購**
        93,358 客戶,只有 1,693 人在 >1 個月買過 —
        **平台級單次客現象**。
        """
    )

st.divider()

st.subheader("💡 業務意涵")
st.error(
    "**回購率不是「低」,而是接近不存在**。"
    "Olist 不缺新客,缺的是讓客回來的理由。"
    "這個發現比 RFM 分群本身更值得 PM / CRM 團隊優先處理。"
)

with st.expander("🤔 三個可驗證假設(留待 v2)"):
    st.markdown(
        """
        - **(a) 巴西電商通病?** 比較 Mercado Livre / Magalu 的留存看是否市場結構問題
        - **(b) 商品結構偏一次性消費?** Olist 主力是家電、家具、寢具 — 一年買一次很正常
        - **(c) 平台未經營會員體系?** 對比有會員 program 的競品(信用卡點數、積分)
        """
    )

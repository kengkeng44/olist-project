"""Olist Brazilian E-Commerce Analytics — Streamlit Dashboard

Run locally:   streamlit run app/Home.py
Deploy:        push to GitHub, deploy from share.streamlit.io
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"

st.set_page_config(
    page_title="Olist 巴西電商分析",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#1a1a2e"
ACCENT = "#e63946"
MUTED = "#94a3b8"


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUTPUT / name, encoding="utf-8-sig")


st.markdown(
    f"""
    <div style='background: linear-gradient(135deg, {PRIMARY} 0%, #16213e 100%);
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.4rem;'>
            🇧🇷 Olist 巴西電商資料分析
        </h1>
        <p style='color: #b8c5d6; margin-top: 0.5rem; font-size: 1.1rem;'>
            從 99K 筆交易找出 <strong style='color: {ACCENT};'>R$ 469K 召回商機</strong>
            與 <strong style='color: {ACCENT};'>平台級留存問題</strong>
        </p>
        <p style='color: #94a3b8; margin-top: 0.3rem; font-size: 0.9rem;'>
            Python · SQL · SQLite · Plotly · Streamlit
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi = load_csv("kpi_yearly.csv")
total_revenue = kpi["總營收_M"].sum()
total_orders = int(kpi["總訂單數"].sum())
avg_rating = (kpi["平均評分"] * kpi["總訂單數"]).sum() / total_orders
avg_delivery = (kpi["平均送達天數"] * kpi["總訂單數"]).sum() / total_orders

c1, c2, c3, c4 = st.columns(4)
c1.metric("總營收", f"R$ {total_revenue:.1f}M", help="2016–2018 累計 GMV")
c2.metric("總訂單數", f"{total_orders:,}")
c3.metric("平均評分", f"{avg_rating:.2f} ★")
c4.metric("平均送達", f"{avg_delivery:.1f} 天")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("📈 月營收趨勢 (2017–2018)")
    rev = load_csv("revenue.csv")
    rev["月份"] = pd.to_datetime(rev["月份"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rev["月份"], y=rev["總營收"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=7, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(26, 26, 46, 0.08)",
        hovertemplate="<b>%{x|%Y-%m}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    fig.add_vline(
        x=pd.Timestamp("2018-09-01"), line_dash="dash",
        line_color=ACCENT, opacity=0.7,
        annotation_text="2018-09 資料截斷", annotation_position="top right",
        annotation_font_color=ACCENT,
    )
    fig.update_layout(
        height=380, margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🏆 三大營收支柱")
    cat = load_csv("category.csv").head(3)
    for _, row in cat.iterrows():
        st.markdown(
            f"""
            <div style='background:#f8fafc; padding:0.8rem 1rem;
                        border-left: 4px solid {ACCENT}; border-radius:6px;
                        margin-bottom: 0.5rem;'>
                <div style='font-size:0.85rem; color:{MUTED};'>{row['商品類別']}</div>
                <div style='font-size:1.3rem; font-weight:bold; color:{PRIMARY};'>
                    R$ {row['總營收']/1000:.0f}K
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

st.subheader("🎯 核心發現一覽")
f1, f2, f3 = st.columns(3)

with f1:
    st.markdown(
        f"""
        <div style='background: white; padding: 1.5rem; border-radius: 10px;
                    border: 1px solid #e2e8f0; height: 100%;'>
            <div style='color: {ACCENT}; font-size: 0.85rem; font-weight: bold;'>
                發現 1️⃣ — 留存
            </div>
            <h3 style='margin: 0.3rem 0; color: {PRIMARY};'>F=1.0 平台級單次客</h3>
            <p style='color: #64748b; font-size: 0.95rem;'>
                93,358 客戶,只有 <strong>1.81%</strong> 跨月回購。
                M1 留存 0.2-0.7%(成熟電商基準 5-15%)。
            </p>
            <a href='/Cohort' target='_self' style='color:{ACCENT}; text-decoration:none;'>→ 看 Cohort 熱力圖</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with f2:
    st.markdown(
        f"""
        <div style='background: white; padding: 1.5rem; border-radius: 10px;
                    border: 1px solid #e2e8f0; height: 100%;'>
            <div style='color: {ACCENT}; font-size: 0.85rem; font-weight: bold;'>
                發現 2️⃣ — 召回 ROI
            </div>
            <h3 style='margin: 0.3rem 0; color: {PRIMARY};'>R$ 469K 機會</h3>
            <p style='color: #64748b; font-size: 0.95rem;'>
                流失風險群 21,975 人佔 <strong>35.5%</strong> 營收。
                召回 20% → R$ 469K → ROI <strong>9.4×</strong>。
            </p>
            <a href='/RFM' target='_self' style='color:{ACCENT}; text-decoration:none;'>→ 看 RFM 分群</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with f3:
    st.markdown(
        f"""
        <div style='background: white; padding: 1.5rem; border-radius: 10px;
                    border: 1px solid #e2e8f0; height: 100%;'>
            <div style='color: {ACCENT}; font-size: 0.85rem; font-weight: bold;'>
                發現 3️⃣ — 巴西特色
            </div>
            <h3 style='margin: 0.3rem 0; color: {PRIMARY};'>分期 = 隱形 CRM</h3>
            <p style='color: #64748b; font-size: 0.95rem;'>
                7-10 期客單 = 一次付清的 <strong>3.48×</strong>,
                回購率高 <strong>65%</strong>。
            </p>
            <a href='/分期付款' target='_self' style='color:{ACCENT}; text-decoration:none;'>→ 看分期分析</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

with st.expander("ℹ️ 關於這份分析"):
    st.markdown(
        """
        **資料來源**:[Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
        範圍 2016-09 ~ 2018-10,9 張表,99,441 筆訂單。

        **方法論差異化**
        - 用 SQL Window Function (NTILE) 做 RFM,而非 Python 套件 — 可移植到 Snowflake / BigQuery
        - 規則式分群而非 K-Means — 業務團隊聽得懂「冠軍客戶」聽不懂「Cluster 3」
        - Insight 量化成 ROI 數字,非空泛建議

        **完整文件**:[GitHub repo](https://github.com/kengkeng44/olist-project)
        含 13 頁簡報 (`slides/portfolio.pdf`) 與分析 Notebook。
        """
    )

st.sidebar.markdown(
    f"""
    ### Olist Analytics

    **作者**:jenho.cheng
    **GitHub**:[kengkeng44/olist-project](https://github.com/kengkeng44/olist-project)
    **Tableau**:[查看 dashboard](https://public.tableau.com/app/profile/jenho.cheng)

    ---

    **分頁說明**
    - 📊 EDA — 規模、付款、評分分布
    - 🗺️ 地理 — 各州營收 + 物流
    - 👥 RFM — 客戶分群 + ROI 試算
    - 📉 Cohort — 留存熱力圖
    - 💳 分期 — 巴西分期付款洞察
    """
)

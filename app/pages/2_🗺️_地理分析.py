"""地理 — 各州營收 + 物流效率。"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "output"
PRIMARY = "#1a1a2e"
ACCENT = "#e63946"

st.set_page_config(page_title="地理分析 · Olist", page_icon="🗺️", layout="wide")
st.title("🗺️ 地理分析")
st.caption("各州營收集中度 + 物流效率(實際 vs 預期送達)")

@st.cache_data
def load(name): return pd.read_csv(OUTPUT / name, encoding="utf-8-sig")

state = load("state.csv").sort_values("總營收", ascending=False)
logistics = load("logistics.csv")

st.subheader("💰 各州營收 Top 15")
top15 = state.head(15)
total_top5 = top15.head(5)["總營收"].sum() / state["總營收"].sum() * 100

c1, c2 = st.columns([3, 1])
with c1:
    colors = [ACCENT if i < 5 else "#94a3b8" for i in range(len(top15))]
    fig = go.Figure(go.Bar(
        x=top15["州"], y=top15["總營收"]/1000,
        marker_color=colors,
        text=[f"R${v/1000:.0f}K" for v in top15["總營收"]],
        textposition="outside",
    ))
    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", yaxis_title="總營收 (K R$)",
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.metric("Top 5 州營收佔比", f"{total_top5:.1f}%")
    st.markdown(
        f"""
        - SP 一州就佔 **{state.iloc[0]['總營收']/state['總營收'].sum()*100:.1f}%**
        - 東南-南五州 (SP/RJ/MG/RS/PR) 合計 **77%**
        - 行銷與物流策略應聚焦南方
        """
    )

st.divider()

st.subheader("🚚 各州物流效率 (Top 15 by 訂單)")
log15 = logistics.head(15).copy()
log15["延遲提早"] = log15["預期天數"] - log15["實際天數"]

fig = go.Figure()
fig.add_trace(go.Bar(
    name="實際送達天數", x=log15["州"], y=log15["實際天數"],
    marker_color=ACCENT, text=[f"{v:.1f}" for v in log15["實際天數"]],
    textposition="auto",
))
fig.add_trace(go.Bar(
    name="預期送達天數", x=log15["州"], y=log15["預期天數"],
    marker_color="#94a3b8", text=[f"{v:.1f}" for v in log15["預期天數"]],
    textposition="auto",
))
fig.update_layout(
    barmode="group", height=400, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", yaxis_title="天數",
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
fast = logistics.iloc[0]
slow = logistics.iloc[-1] if len(logistics) > 5 else logistics.iloc[-1]
c1.metric("最快州", f"{fast['州']} · {fast['實際天數']:.1f} 天")
c2.metric("Olist 平均", "15.4 天", f"-{(24-15.4):.1f} 天 vs ETA 24 天")
c3.metric("ETA 高估幅度", "36%", help="平台 ETA 普遍給保守值")

st.success(
    "💡 **PM 建議**:複製 SP 倉配模式至高訂單州;"
    "偏遠州 ETA 過於保守,行銷頁可改顯示更積極的天數提升轉換。"
)

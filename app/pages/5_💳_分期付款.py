"""巴西分期付款洞察 — Olist 資料的差異化賣點。"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "output"
PRIMARY = "#1a1a2e"
ACCENT = "#e63946"

st.set_page_config(page_title="分期付款 · Olist", page_icon="💳", layout="wide")
st.title("💳 巴西分期付款洞察")
st.caption("Olist 資料的差異化賣點 · 76,795 筆信用卡訂單")

@st.cache_data
def load(name): return pd.read_csv(OUTPUT / name, encoding="utf-8-sig")

inst = load("installments.csv")
inst.columns = ["bucket", "sort_key", "orders", "avg_ticket", "customers", "repeat_rate_pct"]
inst = inst.sort_values("sort_key")

c1, c2, c3, c4 = st.columns(4)
hi = inst[inst["bucket"] == "7-10 期"].iloc[0]
lo = inst[inst["bucket"] == "1 (一次付清)"].iloc[0]
c1.metric("ARPU 倍數", f"{hi['avg_ticket']/lo['avg_ticket']:.2f}×",
          help="7-10 期 vs 一次付清")
c2.metric("回購率提升", f"{(hi['repeat_rate_pct']/lo['repeat_rate_pct']-1)*100:.0f}%",
          help="7-10 期 vs 一次付清")
c3.metric("7+ 期客戶數", f"{int(inst[inst['sort_key']>=7]['customers'].sum()):,}")
c4.metric("信用卡訂單佔比", "73.9%", help="vs Boleto 19%, Voucher 5.6%")

st.divider()

c1, c2 = st.columns(2)
colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]

with c1:
    st.subheader("📈 分期數 → 客單價")
    fig = go.Figure(go.Bar(
        x=inst["bucket"], y=inst["avg_ticket"],
        marker_color=colors,
        text=[f"R$ {v:.0f}" for v in inst["avg_ticket"]],
        textposition="outside",
        customdata=inst["orders"],
        hovertemplate="<b>%{x}</b><br>平均客單 R$ %{y:.0f}<br>訂單數 %{customdata:,}<extra></extra>",
    ))
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", yaxis_title="平均客單 (R$)",
        yaxis=dict(range=[0, inst["avg_ticket"].max()*1.18]),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"7-10 期客單 R${hi['avg_ticket']:.0f} = 一次付清的 {hi['avg_ticket']/lo['avg_ticket']:.2f} 倍 · 線性增長")

with c2:
    st.subheader("🔁 分期數 → 回購率")
    fig = go.Figure(go.Bar(
        x=inst["bucket"], y=inst["repeat_rate_pct"],
        marker_color=colors,
        text=[f"{v:.2f}%" for v in inst["repeat_rate_pct"]],
        textposition="outside",
        customdata=inst["customers"],
        hovertemplate="<b>%{x}</b><br>回購率 %{y:.2f}%<br>客戶數 %{customdata:,}<extra></extra>",
    ))
    baseline = lo["repeat_rate_pct"]
    fig.add_hline(
        y=baseline, line_dash="dash", line_color="gray", opacity=0.6,
        annotation_text=f"baseline {baseline:.2f}%", annotation_position="bottom right",
    )
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", yaxis_title="回購率 (%)",
        yaxis=dict(range=[0, inst["repeat_rate_pct"].max()*1.25]),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"7+ 期客戶回購率 {hi['repeat_rate_pct']:.2f}% = 一次付清的 {hi['repeat_rate_pct']/lo['repeat_rate_pct']:.2f} 倍")

st.divider()

st.subheader("📋 完整數據")
display = inst[["bucket", "orders", "avg_ticket", "customers", "repeat_rate_pct"]].copy()
display["orders"] = display["orders"].apply(lambda v: f"{int(v):,}")
display["avg_ticket"] = display["avg_ticket"].apply(lambda v: f"R$ {v:.0f}")
display["customers"] = display["customers"].apply(lambda v: f"{int(v):,}")
display["repeat_rate_pct"] = display["repeat_rate_pct"].apply(lambda v: f"{v:.2f}%")
display.columns = ["分期數", "訂單數", "平均客單", "客戶數", "回購率"]
st.dataframe(display, hide_index=True, use_container_width=True)

st.divider()

st.subheader("💡 業務意涵 — 分期是 Olist 的隱形 CRM")
c1, c2 = st.columns(2)
with c1:
    st.success(
        "**收入槓桿** — 推廣分期方案直接拉高 GMV"
    )
    st.success(
        "**留存槓桿** — 分期客戶因「未付清」與平台維持帳務關係,自然降低流失"
    )
with c2:
    st.markdown(
        """
        **PM 可落地行動**
        1. 首頁/結帳頁更積極推銷 7+ 期方案(目前僅佔信用卡訂單 15%)
        2. 首單一次付清的客戶,第二次到訪推「無息分期」EDM
        3. 與發卡銀行談更長免息期(現有甜蜜點 8 期 n=4,268,測試 12 期能否拉動更高 ARPU)
        """
    )

st.warning(
    "⚠️ **限制**:因果方向未證實 — 可能是「客單高 → 必須分期」而非「分期 → 客單高」。"
    "需 A/B 測試在相同商品頁強制分期 vs 不分期看轉換差異。"
)

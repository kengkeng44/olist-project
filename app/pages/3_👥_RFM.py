"""RFM 分群 + 互動 ROI 試算。"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "output"
PRIMARY = "#1a1a2e"
ACCENT = "#e63946"

st.set_page_config(page_title="RFM · Olist", page_icon="👥", layout="wide")
st.title("👥 RFM 客戶分群 + 召回 ROI 試算")
st.caption("NTILE(5) Window Function + 規則式分群 · 量化召回機會")

@st.cache_data
def load(name): return pd.read_csv(OUTPUT / name, encoding="utf-8-sig")

rfm = load("rfm_segments.csv").sort_values("營收佔比_%", ascending=False)

st.subheader("🎯 6 個分群結果")

c1, c2 = st.columns([3, 2])
with c1:
    fig = px.treemap(
        rfm, path=["segment"], values="營收佔比_%", color="平均_M_元",
        color_continuous_scale=["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
        custom_data=["客戶佔比_%", "平均_R_天", "平均_M_元"],
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>營收 %{value:.1f}%<br>客戶 %{customdata[0]:.1f}%",
        hovertemplate="<b>%{label}</b><br>營收佔比 %{value:.1f}%<br>"
                      "客戶佔比 %{customdata[0]:.1f}%<br>"
                      "平均 R %{customdata[1]:.0f} 天<br>"
                      "ARPU R$ %{customdata[2]:.0f}<extra></extra>",
        textfont_size=14,
    )
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("面積 = 營收佔比 · 顏色深度 = ARPU")

with c2:
    st.markdown("**Pareto 法則成立**")
    pareto = rfm[rfm["segment"].isin(["冠軍客戶", "流失風險"])]
    st.markdown(
        f"""
        🏆 冠軍 + ⚠️ 流失風險 =
        - **{pareto['客戶佔比_%'].sum():.1f}%** 客戶
        - **{pareto['營收佔比_%'].sum():.1f}%** 營收

        → 行銷預算應集中此兩群
        """
    )
    st.markdown("**🚨 致命發現**")
    st.warning(
        f"所有 segment 的 F (回購頻率) 都 ≈ 1.0"
        f"(平均 {rfm['平均_F_次'].mean():.2f})"
        f" — Olist 處於**獲客驅動**而非**留存驅動**階段。"
    )

st.divider()

st.subheader("📋 分群詳情")
display = rfm.copy()
display["平均_M_元"] = display["平均_M_元"].apply(lambda v: f"R$ {v:,.0f}")
display["平均_R_天"] = display["平均_R_天"].apply(lambda v: f"{v:.0f} 天")
display["客戶數"] = display["客戶數"].apply(lambda v: f"{int(v):,}")
display["群組總營收"] = display["群組總營收"].apply(lambda v: f"R$ {v/1000:,.0f}K")
display.columns = ["分群", "客戶數", "平均 R", "平均 F", "ARPU", "群組營收", "營收 %", "客戶 %"]
st.dataframe(display, hide_index=True, use_container_width=True)

st.divider()

st.subheader("💰 召回 ROI 試算機")
st.caption("拖動下方參數,即時計算流失風險群召回的 ROI")

risk = rfm[rfm["segment"] == "流失風險"].iloc[0]
risk_n = int(risk["客戶數"])
risk_arpu = float(risk["平均_M_元"])

c1, c2, c3 = st.columns(3)
with c1:
    recall_rate = st.slider("召回率 (%)", 1, 30, 10, help="EDM 觸及後實際回購的比例")
with c2:
    cost = st.number_input("CRM 成本 (R$)", 10000, 200000, 50000, step=10000)
with c3:
    repeat_pct = st.slider("回購金額 (% of ARPU)", 20, 100, 50,
                           help="保守估計,避免高估")

recalled = int(risk_n * recall_rate / 100)
incremental = recalled * risk_arpu * (repeat_pct / 100)
roi = incremental / cost

m1, m2, m3, m4 = st.columns(4)
m1.metric("流失風險客戶數", f"{risk_n:,}")
m2.metric("預期召回人數", f"{recalled:,}")
m3.metric("增量營收", f"R$ {incremental/1000:.0f}K")
m4.metric("ROI", f"{roi:.2f}×",
          delta=f"{'高' if roi > 5 else '中' if roi > 2 else '低'}",
          delta_color="normal" if roi > 2 else "inverse")

if roi > 5:
    st.success(f"🚀 **強烈建議執行** — 預期淨收益 R$ {(incremental-cost)/1000:.0f}K")
elif roi > 2:
    st.info(f"✅ **建議執行** — 預期淨收益 R$ {(incremental-cost)/1000:.0f}K")
else:
    st.warning("⚠️ ROI 偏低,建議先做小規模 A/B 測試驗證假設")

with st.expander("📐 計算公式 & 假設"):
    st.markdown(
        f"""
        ```
        增量營收 = 召回人數 × ARPU × 回購比例
                = {recalled:,} × R$ {risk_arpu:.0f} × {repeat_pct}%
                = R$ {incremental:,.0f}

        ROI = 增量營收 / 成本
            = R$ {incremental:,.0f} / R$ {cost:,.0f}
            = {roi:.2f}×
        ```

        **假設限制**
        - 召回客戶若回購,金額為其歷史 ARPU 的 {repeat_pct}%(保守估計)
        - CRM 成本含 EDM、折扣券、人力,不含後續客服
        - 未考慮品牌效應(召回失敗的客戶仍可能因為觸及而提升 NPS)
        """
    )

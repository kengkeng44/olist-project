"""EDA — 資料規模、付款結構、評分分布、年度成長。"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "output"
PRIMARY = "#1a1a2e"
ACCENT = "#e63946"

st.set_page_config(page_title="EDA · Olist", page_icon="📊", layout="wide")
st.title("📊 資料概況 (EDA)")
st.caption("規模快照、訂單狀態、付款結構、評分分布")


@st.cache_data
def load(name): return pd.read_csv(OUTPUT / name, encoding="utf-8-sig")


st.subheader("規模快照")
c = st.columns(6)
metrics = [
    ("訂單數", "99,441"), ("Unique 客戶", "96,096"),
    ("賣家數", "3,095"), ("商品數", "32,951"),
    ("商品類目", "71"), ("涵蓋州", "27 (全境)"),
]
for col, (label, val) in zip(c, metrics):
    col.metric(label, val)

st.info(
    "⚠️ **`customer_id` ≠ `customer_unique_id`** — 每筆訂單會生新的 customer_id"
    " (n=99,441),但實際只有 96,096 個 unique 客戶。RFM 必須用 unique_id 才不會誤算。"
)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("📅 年度成長 (2017 vs 2018)")
    growth = load("growth.csv").iloc[0]
    df_growth = pd.DataFrame({
        "指標": ["營收 (M R$)", "訂單數 (K)", "平均評分"],
        "2017": [growth["營收_2017"], growth["訂單_2017"]/1000, growth["評分_2017"]],
        "2018": [growth["營收_2018"], growth["訂單_2018"]/1000, growth["評分_2018"]],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(name="2017", x=df_growth["指標"], y=df_growth["2017"],
                          marker_color="#94a3b8"))
    fig.add_trace(go.Bar(name="2018", x=df_growth["指標"], y=df_growth["2018"],
                          marker_color=ACCENT))
    fig.update_layout(barmode="group", height=350, margin=dict(l=10, r=10, t=10, b=10),
                      plot_bgcolor="white", legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("2018 年僅統計到 10 月,實際全年成長更高。")

with right:
    st.subheader("⭐ 評分分布")
    rev = load("reviews.csv")
    rev["佔比"] = rev["數量"] / rev["數量"].sum() * 100
    rev = rev.sort_values("評分", ascending=True)
    colors = ["#dc2626", "#ea580c", "#facc15", "#84cc16", "#16a34a"]
    fig = go.Figure(go.Bar(
        y=[f"{int(s)} ★" for s in rev["評分"]], x=rev["佔比"],
        orientation="h", marker_color=colors,
        text=[f"{p:.1f}%" for p in rev["佔比"]], textposition="outside",
    ))
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                      plot_bgcolor="white", xaxis_title="佔比 (%)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("5 星佔 58%,1 星仍有 12% — 1 星訂單值得交叉物流延遲、商品描述做根因分析。")

st.divider()

st.subheader("💳 付款結構 (巴西特色)")
pay = pd.DataFrame({
    "付款方式": ["credit_card", "boleto", "voucher", "debit_card"],
    "筆數": [76795, 19784, 5775, 1529],
    "佔比 %": [73.9, 19.0, 5.6, 1.5],
    "平均分期數": [3.5, 1.0, 1.0, 1.0],
})

c1, c2 = st.columns([2, 3])
with c1:
    fig = go.Figure(go.Pie(
        labels=pay["付款方式"], values=pay["筆數"],
        hole=0.5, marker=dict(colors=[ACCENT, "#94a3b8", "#cbd5e1", "#e2e8f0"]),
        textinfo="label+percent",
    ))
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.dataframe(pay, hide_index=True, use_container_width=True)
    st.markdown(
        f"""
        > **Boleto** 是巴西特有的「印出繳費單到便利商店繳現金」方式。
        > 不像台灣的 ATM 即時轉帳 — 客戶下單後通常要 1-3 天才完成付款。

        > **平均 3.5 期信用卡**反映巴西強勢的分期文化。
        > <a href='/分期付款' target='_self' style='color:{ACCENT};'>→ 詳見分期付款分析</a>
        """,
        unsafe_allow_html=True,
    )

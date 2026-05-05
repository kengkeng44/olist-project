"""Build a self-contained Tableau-style HTML dashboard.

Loads pre-aggregated CSVs from output/, renders 4 KPI cards + 3 Plotly charts,
writes a single HTML file to docs/index.html for GitHub Pages hosting.

Run:  python notebook/build_dashboard_html.py
Out:  docs/index.html
"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
DOCS = ROOT / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

PRIMARY = "#1a1a2e"
ACCENT = "#e63946"
MUTED = "#94a3b8"
BG = "#f8fafc"

PLOT_KW = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="'Microsoft JhengHei', 'Helvetica Neue', sans-serif", size=12, color=PRIMARY),
    margin=dict(l=20, r=20, t=20, b=20),
)


def fig_to_div(fig, height=380):
    fig.update_layout(height=height, **PLOT_KW)
    return pio.to_html(fig, include_plotlyjs=False, full_html=False,
                       config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]})


# ------------------------- KPI numbers -------------------------
kpi = pd.read_csv(OUT / "kpi_yearly.csv", encoding="utf-8-sig")
total_revenue_m = kpi["總營收_M"].sum()
total_orders = int(kpi["總訂單數"].sum())
avg_rating = (kpi["平均評分"] * kpi["總訂單數"]).sum() / total_orders
avg_delivery = (kpi["平均送達天數"] * kpi["總訂單數"]).sum() / total_orders
aov = total_revenue_m * 1_000_000 / total_orders

# ------------------------- Chart 1: monthly revenue -------------------------
rev = pd.read_csv(OUT / "revenue.csv", encoding="utf-8-sig")
rev["月份"] = pd.to_datetime(rev["月份"])
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=rev["月份"], y=rev["總營收"],
    mode="lines+markers",
    line=dict(color=PRIMARY, width=3),
    marker=dict(size=7, color=ACCENT),
    fill="tozeroy", fillcolor="rgba(26,26,46,0.08)",
    hovertemplate="<b>%{x|%Y-%m}</b><br>R$ %{y:,.0f}<extra></extra>",
))
fig1.add_vline(
    x=pd.Timestamp("2018-09-01").timestamp() * 1000,
    line_dash="dash", line_color=ACCENT, opacity=0.7,
    annotation_text="2018-09 資料截斷", annotation_position="top right",
    annotation_font_color=ACCENT,
)
fig1.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="總營收 (R$)"),
    hovermode="x unified",
)
chart1_html = fig_to_div(fig1, height=400)

# ------------------------- Chart 2: state revenue (Top 15 horizontal) -------------------------
state = pd.read_csv(OUT / "state.csv", encoding="utf-8-sig").sort_values("總營收", ascending=True)
top15 = state.tail(15)
colors = [ACCENT if i >= 10 else MUTED for i in range(len(top15))]
fig2 = go.Figure(go.Bar(
    y=top15["州"], x=top15["總營收"]/1000,
    orientation="h",
    marker_color=colors,
    text=[f"R$ {v/1000:.0f}K" for v in top15["總營收"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}K<extra></extra>",
))
fig2.update_layout(
    xaxis_title="總營收 (千 R$)", yaxis_title=None,
    showlegend=False,
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=False),
)
chart2_html = fig_to_div(fig2, height=400)

# ------------------------- Chart 3: RFM treemap -------------------------
rfm = pd.read_csv(OUT / "rfm_segments.csv", encoding="utf-8-sig").sort_values("營收佔比_%", ascending=False)
fig3 = px.treemap(
    rfm, path=["segment"], values="營收佔比_%",
    color="平均_M_元",
    color_continuous_scale=["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
    custom_data=["客戶佔比_%", "平均_R_天", "平均_M_元"],
)
fig3.update_traces(
    texttemplate="<b>%{label}</b><br>營收 %{value:.1f}%<br>客戶 %{customdata[0]:.1f}%",
    hovertemplate="<b>%{label}</b><br>營收佔比 %{value:.1f}%<br>"
                  "客戶佔比 %{customdata[0]:.1f}%<br>"
                  "平均 R %{customdata[1]:.0f} 天<br>"
                  "ARPU R$ %{customdata[2]:.0f}<extra></extra>",
    textfont_size=14,
)
chart3_html = fig_to_div(fig3, height=400)

# ------------------------- HTML template -------------------------
html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Olist 巴西電商分析 · Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Microsoft JhengHei', 'Helvetica Neue', -apple-system, sans-serif;
      background: {BG};
      color: {PRIMARY};
      line-height: 1.5;
    }}
    .header {{
      background: linear-gradient(135deg, {PRIMARY} 0%, #16213e 100%);
      color: white;
      padding: 2rem 2.5rem;
    }}
    .header h1 {{ margin: 0; font-size: 2rem; font-weight: 700; }}
    .header .subtitle {{ color: #b8c5d6; margin-top: 0.4rem; font-size: 1rem; }}
    .header .meta {{ color: #94a3b8; margin-top: 0.3rem; font-size: 0.85rem; }}
    .header a {{ color: {ACCENT}; text-decoration: none; }}
    .header a:hover {{ text-decoration: underline; }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
    }}

    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}
    .kpi-card {{
      background: white;
      border-radius: 10px;
      padding: 1.4rem 1.6rem;
      border-left: 4px solid {ACCENT};
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .kpi-label {{
      font-size: 0.8rem;
      color: {MUTED};
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.4rem;
    }}
    .kpi-value {{
      font-size: 2rem;
      font-weight: 700;
      color: {PRIMARY};
      line-height: 1;
    }}
    .kpi-help {{
      font-size: 0.78rem;
      color: {MUTED};
      margin-top: 0.4rem;
    }}

    .chart-row {{
      display: grid;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}
    .chart-row.full {{ grid-template-columns: 1fr; }}
    .chart-row.split {{ grid-template-columns: 1fr 1fr; }}

    .chart-card {{
      background: white;
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .chart-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: {PRIMARY};
      margin: 0 0 0.2rem 0;
    }}
    .chart-subtitle {{
      font-size: 0.85rem;
      color: {MUTED};
      margin-bottom: 1rem;
    }}

    .footer {{
      text-align: center;
      color: {MUTED};
      font-size: 0.8rem;
      padding: 1.5rem 1rem 2rem 1rem;
      border-top: 1px solid #e2e8f0;
      margin-top: 2rem;
    }}
    .footer a {{ color: {ACCENT}; text-decoration: none; }}
    .footer a:hover {{ text-decoration: underline; }}

    @media (max-width: 900px) {{
      .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
      .chart-row.split {{ grid-template-columns: 1fr; }}
      .header h1 {{ font-size: 1.5rem; }}
      .kpi-value {{ font-size: 1.5rem; }}
    }}
  </style>
</head>
<body>

<div class="header">
  <h1>🇧🇷 Olist 巴西電商分析 · Dashboard</h1>
  <div class="subtitle">99,441 筆訂單 · 27 州 · R$ 469K 召回機會 (ROI 9.4×)</div>
  <div class="meta">
    2016–2018 · 資料來源 Brazilian E-Commerce Public Dataset by Olist (Kaggle, CC-BY-NC-SA 4.0)
    · 作者 jenho.cheng · <a href="https://github.com/kengkeng44/olist-project">GitHub repo ↗</a>
    · <a href="https://olist-jenho.streamlit.app/">Streamlit 互動版 ↗</a>
  </div>
</div>

<div class="container">

  <!-- KPI cards -->
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">總營收</div>
      <div class="kpi-value">R$ {total_revenue_m:.1f}M</div>
      <div class="kpi-help">2016–2018 累計 GMV</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">總訂單數</div>
      <div class="kpi-value">{total_orders:,}</div>
      <div class="kpi-help">跨 27 州、4,119 城市</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">平均客單</div>
      <div class="kpi-value">R$ {aov:.0f}</div>
      <div class="kpi-help">每筆訂單平均</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">客戶滿意度</div>
      <div class="kpi-value">{avg_rating:.2f} ★</div>
      <div class="kpi-help">加權平均(2017–2018)</div>
    </div>
  </div>

  <!-- Chart 1: full width -->
  <div class="chart-row full">
    <div class="chart-card">
      <h3 class="chart-title">月營收趨勢 2017–2018</h3>
      <p class="chart-subtitle">2017 Q4 (黑五+聖誕) 達高峰 R$ 1M;2018 進入穩定期 0.7–1.0M。
         2018-09 後為資料截斷,非真實衰退。</p>
      {chart1_html}
    </div>
  </div>

  <!-- Chart 2 + 3: split -->
  <div class="chart-row split">
    <div class="chart-card">
      <h3 class="chart-title">各州營收 Top 15</h3>
      <p class="chart-subtitle">SP 一州佔 41.9%,東南-南五州 (SP/RJ/MG/RS/PR) 合計 77%。
         紅色為 Top 5,行銷策略應聚焦南方。</p>
      {chart2_html}
    </div>
    <div class="chart-card">
      <h3 class="chart-title">RFM 6 分群 — 客戶營收貢獻</h3>
      <p class="chart-subtitle">面積 = 營收佔比,顏色深度 = ARPU。
         冠軍 + 流失風險合佔 67% 營收 → 召回 ROI 9.4× 主要機會。</p>
      {chart3_html}
    </div>
  </div>

</div>

<div class="footer">
  Generated with Python + Plotly · Source on
  <a href="https://github.com/kengkeng44/olist-project">GitHub</a>
  · <a href="https://github.com/kengkeng44/olist-project/blob/master/notebook/build_dashboard_html.py">build script</a>
  <br>
  互動式進階版 → <a href="https://olist-jenho.streamlit.app/">Streamlit</a>
  · 13 頁簡報 → <a href="https://github.com/kengkeng44/olist-project/blob/master/slides/portfolio.pdf">PDF</a>
  · 召回提案 PRD → <a href="https://github.com/kengkeng44/olist-project/blob/master/proposals/recall_campaign_prd.md">Markdown</a>
</div>

</body>
</html>
"""

(DOCS / "index.html").write_text(html, encoding="utf-8")
print(f"saved: {DOCS / 'index.html'}")
print(f"size:  {(DOCS / 'index.html').stat().st_size / 1024:.1f} KB")

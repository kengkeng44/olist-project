"""Generate output/portfolio.xlsx — 10-sheet resume-ready Excel for e-commerce interviews.

Builds: Cover, Executive Summary, KPIs, Revenue Trend, RFM, Cohort Heatmap,
ROI Calculator (live formulas), Installments, Logistics, Methodology.
"""
from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
XLSX_PATH = OUTPUT_DIR / "portfolio.xlsx"

# ---------- Style palette ----------
NAVY = "1F3A5F"
TEAL = "2E8B8B"
ORANGE = "E07B39"
LIGHT_GRAY = "F2F2F2"
DARK_GRAY = "595959"
WHITE = "FFFFFF"
ACCENT_YELLOW = "F4D35E"

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def font(*, size=11, bold=False, color="000000", italic=False) -> Font:
    return Font(name="Calibri", size=size, bold=bold, color=color, italic=italic)


def fill(color: str) -> PatternFill:
    return PatternFill("solid", fgColor=color)


def center() -> Alignment:
    return Alignment(horizontal="center", vertical="center", wrap_text=True)


def left() -> Alignment:
    return Alignment(horizontal="left", vertical="center", wrap_text=True)


def right() -> Alignment:
    return Alignment(horizontal="right", vertical="center", wrap_text=True)


def header_row(ws: Worksheet, row: int, cols: list[str], start_col: int = 1) -> None:
    for i, label in enumerate(cols):
        c = ws.cell(row=row, column=start_col + i, value=label)
        c.font = font(bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = center()
        c.border = BORDER


def section_title(ws: Worksheet, row: int, text: str, span: int = 6) -> None:
    ws.cell(row=row, column=1, value=text).font = font(size=14, bold=True, color=NAVY)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)


def set_col_widths(ws: Worksheet, widths: dict[str, float]) -> None:
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUTPUT_DIR / name).open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ============================================================================
# Sheet 1 — Cover
# ============================================================================
def build_cover(wb: Workbook) -> None:
    ws = wb.create_sheet("1. Cover")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 28, "C": 28, "D": 28, "E": 28, "F": 2})

    # Title block
    ws.row_dimensions[2].height = 40
    ws.cell(row=2, column=2, value="Olist Brazilian E-Commerce").font = font(size=26, bold=True, color=NAVY)
    ws.merge_cells("B2:E2")

    ws.row_dimensions[3].height = 26
    ws.cell(row=3, column=2, value="End-to-End Customer Analytics — SQL · RFM · Cohort · ROI").font = font(
        size=14, italic=True, color=DARK_GRAY
    )
    ws.merge_cells("B3:E3")

    ws.cell(row=5, column=2, value="Author").font = font(bold=True, color=NAVY)
    ws.cell(row=5, column=3, value="Jen-Ho Cheng").font = font()
    ws.cell(row=6, column=2, value="Role").font = font(bold=True, color=NAVY)
    ws.cell(row=6, column=3, value="Data / Product Analyst — E-commerce").font = font()
    ws.cell(row=7, column=2, value="Dataset").font = font(bold=True, color=NAVY)
    ws.cell(row=7, column=3, value="Olist (Brazil) · 99,441 orders · 2016–2018").font = font()

    # Headline metrics (3 big cards)
    ws.cell(row=10, column=2, value="THREE HEADLINE FINDINGS").font = font(size=12, bold=True, color=NAVY)

    cards = [
        ("R$ 469K", "Win-back revenue opportunity", "21,975 at-risk customers · 9.4× ROI in aggressive scenario"),
        ("1.81%", "Cross-month repeat rate", "Platform-level retention failure (vs. 5–15% mature benchmark)"),
        ("3.48×", "ARPU lift from 7-10 installments", "R$ 334 vs R$ 96 single payment — Brazil's hidden CRM"),
    ]
    for i, (big, mid, small) in enumerate(cards):
        col = 2 + i
        ws.row_dimensions[12].height = 38
        ws.row_dimensions[13].height = 22
        ws.row_dimensions[14].height = 36
        c = ws.cell(row=12, column=col, value=big)
        c.font = font(size=24, bold=True, color=WHITE)
        c.fill = fill([NAVY, TEAL, ORANGE][i])
        c.alignment = center()
        c.border = BORDER
        c2 = ws.cell(row=13, column=col, value=mid)
        c2.font = font(size=11, bold=True, color=WHITE)
        c2.fill = fill([NAVY, TEAL, ORANGE][i])
        c2.alignment = center()
        c2.border = BORDER
        c3 = ws.cell(row=14, column=col, value=small)
        c3.font = font(size=9, color="000000")
        c3.fill = fill(LIGHT_GRAY)
        c3.alignment = center()
        c3.border = BORDER

    # Links
    ws.cell(row=17, column=2, value="LIVE LINKS").font = font(size=12, bold=True, color=NAVY)
    links = [
        ("Streamlit App", "https://olist-jenho.streamlit.app/", "Interactive 5-page dashboard with ROI calculator"),
        ("HTML Dashboard", "https://kengkeng44.github.io/olist-project/", "Static GitHub Pages site"),
        ("Tableau Public", "https://public.tableau.com/app/profile/jenho.cheng/viz/2_17739060990590/1?publish=yes", "Tableau visualization"),
        ("GitHub Repo", "https://github.com/kengkeng44/olist-project", "Full source code + Notebook + SQL"),
        ("Pitch Deck (PDF)", "https://github.com/kengkeng44/olist-project/blob/master/slides/portfolio.pdf", "13-slide PM-style deck"),
    ]
    header_row(ws, 18, ["Resource", "URL", "What you'll find"])
    for i, (label, url, desc) in enumerate(links):
        r = 19 + i
        ws.cell(row=r, column=2, value=label).font = font(bold=True)
        c = ws.cell(row=r, column=3, value=url)
        c.hyperlink = url
        c.font = font(color="0563C1")
        c.alignment = left()
        ws.cell(row=r, column=4, value=desc).alignment = left()
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = BORDER

    # Tech stack chips
    ws.cell(row=26, column=2, value="TECH STACK").font = font(size=12, bold=True, color=NAVY)
    stack = ["Python", "SQLite", "SQL (NTILE Window)", "pandas", "matplotlib", "Streamlit", "Tableau"]
    for i, t in enumerate(stack):
        c = ws.cell(row=27, column=2 + i % 4, value=t) if i < 4 else ws.cell(row=28, column=2 + (i - 4), value=t)
        c.font = font(bold=True, color=NAVY)
        c.fill = fill(ACCENT_YELLOW)
        c.alignment = center()
        c.border = BORDER


# ============================================================================
# Sheet 2 — Executive Summary
# ============================================================================
def build_summary(wb: Workbook) -> None:
    ws = wb.create_sheet("2. Executive Summary")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 18, "C": 60, "D": 2})

    ws.cell(row=2, column=2, value="Executive Summary").font = font(size=20, bold=True, color=NAVY)
    ws.merge_cells("B2:C2")
    ws.cell(row=3, column=2, value="One-page brief for hiring managers — read in 60 seconds").font = font(
        size=11, italic=True, color=DARK_GRAY
    )
    ws.merge_cells("B3:C3")

    blocks = [
        ("Question",
         "Brazil's largest SMB marketplace (Olist, 12,000+ sellers) released 99K orders 2016–2018. "
         "Where can the platform unlock the biggest revenue lever next quarter?"),
        ("Method",
         "9-table SQLite schema · SQL Window Functions (NTILE) for RFM scoring · Cohort retention · "
         "Installment-bucket analysis · Quantified ROI scenarios."),
        ("Finding 1 — Pareto",
         "Champions (16% of customers) + At-Risk (24%) drive 67% of revenue. Marketing spend should consolidate here, not chase the long tail."),
        ("Finding 2 — Retention crisis",
         "Cross-month repeat rate is 1.81%. Cohort heatmap shows M1 at 0.2–0.7%. Olist is acquisition-driven, not retention-driven — biggest leverage is win-back, not new acquisition."),
        ("Finding 3 — Installments = hidden CRM",
         "Customers paying in 7–10 installments have 3.48× ARPU and 65% higher repeat rate than single-payment buyers. Installment plans are an under-leveraged retention mechanism."),
        ("Recommendation",
         "Launch personalized win-back EDM to 21,975 At-Risk customers (cost ≈ R$ 50K). Conservative 5% recall = R$ 117K incremental revenue (2.3× ROI). Aggressive 20% = R$ 469K (9.4× ROI)."),
        ("Decision artifact",
         "PRD-style proposal in proposals/recall_campaign_prd.md — includes timeline, cross-team RACI, A/B design, kill criteria. See Sheet 7 for the live ROI calculator."),
    ]
    for i, (label, body) in enumerate(blocks):
        r = 5 + i
        ws.row_dimensions[r].height = 56
        cell_l = ws.cell(row=r, column=2, value=label)
        cell_l.font = font(bold=True, color=WHITE)
        cell_l.fill = fill(NAVY if i < 2 else (TEAL if i < 5 else ORANGE))
        cell_l.alignment = center()
        cell_l.border = BORDER
        cell_b = ws.cell(row=r, column=3, value=body)
        cell_b.font = font(size=11)
        cell_b.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell_b.fill = fill(LIGHT_GRAY)
        cell_b.border = BORDER


# ============================================================================
# Sheet 3 — KPIs / Data Overview
# ============================================================================
def build_kpis(wb: Workbook) -> None:
    ws = wb.create_sheet("3. KPIs")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 30, "C": 18, "D": 18, "E": 18, "F": 18, "G": 2})

    ws.cell(row=2, column=2, value="Data Overview & KPIs").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:F2")

    section_title(ws, 4, "Scale & Coverage", span=6)
    overview = [
        ("Total orders", "99,441"),
        ("Unique customers", "96,096"),
        ("Sellers", "3,095"),
        ("Products", "32,951"),
        ("Product categories", "71"),
        ("States covered", "27 (entire Brazil)"),
        ("Cities covered", "4,119"),
        ("Time range", "2016-09 → 2018-10"),
        ("Total GMV", "R$ 13.1M"),
        ("Avg order value (delivered)", "≈ R$ 137"),
    ]
    header_row(ws, 5, ["Metric", "Value"], start_col=2)
    for i, (k, v) in enumerate(overview):
        r = 6 + i
        ws.cell(row=r, column=2, value=k).font = font(bold=True)
        ws.cell(row=r, column=2).fill = fill(LIGHT_GRAY)
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=2).alignment = left()
        c = ws.cell(row=r, column=3, value=v)
        c.font = font()
        c.alignment = right()
        c.border = BORDER

    # Yearly KPIs table from kpi_yearly.csv
    section_title(ws, 18, "Year-over-Year KPIs", span=6)
    yearly = read_csv("kpi_yearly.csv")
    header_row(ws, 19, ["Year", "GMV (R$ M)", "Orders", "Avg Review", "Avg Delivery (days)"], start_col=2)
    en_map = {"年份": "Year", "總營收_M": "GMV", "總訂單數": "Orders", "平均評分": "Review", "平均送達天數": "Delivery"}
    for i, row in enumerate(yearly):
        r = 20 + i
        ws.cell(row=r, column=2, value=row["年份"]).font = font(bold=True)
        ws.cell(row=r, column=3, value=float(row["總營收_M"]))
        ws.cell(row=r, column=4, value=int(row["總訂單數"]))
        ws.cell(row=r, column=5, value=float(row["平均評分"]))
        ws.cell(row=r, column=6, value=float(row["平均送達天數"]))
        for col in range(2, 7):
            cell = ws.cell(row=r, column=col)
            cell.border = BORDER
            cell.alignment = center() if col > 2 else left()
        ws.cell(row=r, column=3).number_format = "0.00"

    # Caveat
    ws.cell(row=25, column=2,
            value="⚠️ Caveat: 2018 data is truncated at 2018-10. Apparent post-Sep dip = data cutoff, not real decline."
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B25:F25")

    # Order status distribution
    section_title(ws, 27, "Order Status Distribution", span=6)
    status = [
        ("delivered", 96478, 97.0),
        ("shipped", 1107, 1.1),
        ("canceled", 625, 0.6),
        ("unavailable", 609, 0.6),
        ("other", 622, 0.6),
    ]
    header_row(ws, 28, ["Status", "Orders", "Share %"], start_col=2)
    for i, (s, o, p) in enumerate(status):
        r = 29 + i
        ws.cell(row=r, column=2, value=s)
        ws.cell(row=r, column=3, value=o).number_format = "#,##0"
        ws.cell(row=r, column=4, value=p / 100).number_format = "0.0%"
        for col in range(2, 5):
            ws.cell(row=r, column=col).border = BORDER

    # Payment mix
    section_title(ws, 35, "Payment Mix (Brazil-specific)", span=6)
    payments = [
        ("credit_card", 76795, 73.9, 3.5),
        ("boleto", 19784, 19.0, 1.0),
        ("voucher", 5775, 5.6, 1.0),
        ("debit_card", 1529, 1.5, 1.0),
    ]
    header_row(ws, 36, ["Payment type", "Orders", "Share %", "Avg installments"], start_col=2)
    for i, (p, o, share, inst) in enumerate(payments):
        r = 37 + i
        ws.cell(row=r, column=2, value=p)
        ws.cell(row=r, column=3, value=o).number_format = "#,##0"
        ws.cell(row=r, column=4, value=share / 100).number_format = "0.0%"
        ws.cell(row=r, column=5, value=inst).number_format = "0.0"
        for col in range(2, 6):
            ws.cell(row=r, column=col).border = BORDER

    ws.cell(row=42, column=2,
            value="Note: 'boleto' is a Brazil-only cash voucher printed at convenience stores. 1–3 day payment lag affects fulfillment timing."
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B42:F42")


# ============================================================================
# Sheet 4 — Monthly Revenue Trend
# ============================================================================
def build_revenue(wb: Workbook) -> None:
    ws = wb.create_sheet("4. Revenue Trend")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 14, "C": 18, "D": 2})

    ws.cell(row=2, column=2, value="Monthly Revenue Trend (2017–2018)").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:C2")

    rev = read_csv("revenue.csv")
    header_row(ws, 4, ["Month", "Revenue (R$)"], start_col=2)
    for i, row in enumerate(rev):
        r = 5 + i
        ws.cell(row=r, column=2, value=row["月份"])
        c = ws.cell(row=r, column=3, value=float(row["總營收"]))
        c.number_format = "#,##0"
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=3).border = BORDER

    # Chart
    chart = LineChart()
    chart.title = "Monthly Revenue (R$) — peak Nov 2017 (Black Friday + Christmas)"
    chart.y_axis.title = "Revenue (R$)"
    chart.x_axis.title = "Month"
    chart.height = 10
    chart.width = 22
    data = Reference(ws, min_col=3, min_row=4, max_row=4 + len(rev), max_col=3)
    cats = Reference(ws, min_col=2, min_row=5, max_row=4 + len(rev))
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.style = 12
    ws.add_chart(chart, "E4")

    # Insight callouts
    insights_row = 4 + len(rev) + 3
    ws.cell(row=insights_row, column=2, value="KEY INSIGHTS").font = font(size=12, bold=True, color=NAVY)
    insights = [
        "Peak: Nov 2017 ≈ R$ 988K (Black Friday + Christmas)",
        "2018 stable plateau: R$ 0.7M – 1.0M monthly",
        "2018-09 onwards = data truncation, not real decline",
        "Top 3 categories drive revenue: health_beauty, watches_gifts, bed_bath_table",
        "Recommendation: front-load marketing budget pre-Q4; concentrate inventory on top-3 categories",
    ]
    for i, t in enumerate(insights):
        ws.cell(row=insights_row + 1 + i, column=2, value=f"• {t}").font = font()
        ws.merge_cells(start_row=insights_row + 1 + i, start_column=2, end_row=insights_row + 1 + i, end_column=3)


# ============================================================================
# Sheet 5 — RFM Segmentation
# ============================================================================
def build_rfm(wb: Workbook) -> None:
    ws = wb.create_sheet("5. RFM Segments")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 22, "C": 14, "D": 14, "E": 14, "F": 14, "G": 18, "H": 14, "I": 14, "J": 2})

    ws.cell(row=2, column=2, value="RFM Customer Segmentation (NTILE Window Function)").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:I2")

    rows = read_csv("rfm_segments.csv")
    seg_map = {
        "冠軍客戶": ("Champions", "🏆", "Big-ticket buyer who ordered last month — protect, upsell"),
        "流失風險": ("At Risk", "⚠️", "High-value customer dormant ~13 months — top win-back priority"),
        "一般客戶": ("Average", "—", "Mid-frequency, mid-value. Cross-sell test bed"),
        "忠誠客戶": ("Loyal Low-spend", "🔁", "Recent + frequent but low ticket. Bundle / category expansion"),
        "已流失": ("Lost", "💤", "Long inactive + low value. Lowest priority"),
        "潛力新客": ("Potential New", "🌱", "Just acquired, low ticket. Onboarding nurture"),
    }

    header_row(ws, 4, ["Segment", "Customers", "Customer %", "Revenue (R$)", "Revenue %", "ARPU (R$)", "Avg Recency (d)", "Persona / Action"], start_col=2)
    # Sort: Champions, At Risk, Loyal, Average, Potential, Lost (business priority order)
    priority = ["冠軍客戶", "流失風險", "忠誠客戶", "一般客戶", "潛力新客", "已流失"]
    rows_sorted = sorted(rows, key=lambda r: priority.index(r["segment"]))

    for i, row in enumerate(rows_sorted):
        r = 5 + i
        en_label, emoji, persona = seg_map[row["segment"]]
        ws.cell(row=r, column=2, value=f"{emoji} {en_label}").font = font(bold=True)
        ws.cell(row=r, column=3, value=int(row["客戶數"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=float(row["客戶佔比_%"]) / 100).number_format = "0.0%"
        ws.cell(row=r, column=5, value=float(row["群組總營收"])).number_format = "#,##0"
        ws.cell(row=r, column=6, value=float(row["營收佔比_%"]) / 100).number_format = "0.0%"
        ws.cell(row=r, column=7, value=float(row["平均_M_元"])).number_format = "0"
        ws.cell(row=r, column=8, value=float(row["平均_R_天"])).number_format = "0"
        ws.cell(row=r, column=9, value=persona).alignment = left()
        for col in range(2, 10):
            ws.cell(row=r, column=col).border = BORDER

    # Bar chart: customer % vs revenue %
    chart = BarChart()
    chart.type = "bar"
    chart.style = 12
    chart.title = "Customer share vs Revenue share — Pareto: Champions+At Risk = 39.7% / 66.9%"
    chart.y_axis.title = "Segment"
    chart.x_axis.title = "Share %"
    chart.height = 10
    chart.width = 22

    data = Reference(ws, min_col=4, min_row=4, max_row=4 + len(rows_sorted), max_col=4)
    chart.add_data(data, titles_from_data=True)
    data2 = Reference(ws, min_col=6, min_row=4, max_row=4 + len(rows_sorted), max_col=6)
    chart.add_data(data2, titles_from_data=True)
    cats = Reference(ws, min_col=2, min_row=5, max_row=4 + len(rows_sorted))
    chart.set_categories(cats)
    ws.add_chart(chart, "B13")

    # Four insights
    ws.cell(row=33, column=2, value="FOUR BUSINESS INSIGHTS").font = font(size=12, bold=True, color=NAVY)
    insights = [
        "1. Pareto holds — Champions (16%) + At-Risk (24%) = 40% of customers but 67% of revenue",
        "2. Biggest lever is WIN-BACK, not acquisition — At-Risk owns 35.5% of revenue and 21,975 wallets",
        "3. Champions ARPU (R$ 274) is 2× platform avg — VIP program + cross-category recommendation candidate",
        "4. CRITICAL — Frequency ≈ 1.0 across ALL segments. Olist is acquisition-driven, not retention-driven (proven in next sheet)",
    ]
    for i, t in enumerate(insights):
        ws.cell(row=34 + i, column=2, value=t).font = font()
        ws.merge_cells(start_row=34 + i, start_column=2, end_row=34 + i, end_column=9)

    # Why rule-based vs K-Means
    ws.cell(row=39, column=2, value="WHY RULE-BASED, NOT K-MEANS?").font = font(size=12, bold=True, color=NAVY)
    why = [
        "1. Business interpretability — marketing teams understand 'At Risk' but not 'Cluster 3'",
        "2. F dimension has no variance (median = 1.0); K-Means would create meaningless clusters",
        "3. Stable thresholds year-over-year — K-Means re-trains drift segment definitions",
    ]
    for i, t in enumerate(why):
        ws.cell(row=40 + i, column=2, value=t).font = font()
        ws.merge_cells(start_row=40 + i, start_column=2, end_row=40 + i, end_column=9)


# ============================================================================
# Sheet 6 — Cohort Retention Heatmap
# ============================================================================
def build_cohort(wb: Workbook) -> None:
    ws = wb.create_sheet("6. Cohort Heatmap")
    ws.sheet_view.showGridLines = False

    ws.cell(row=2, column=2, value="Cohort Retention Heatmap — Proof of F=1.0").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:O2")
    ws.cell(row=3, column=2,
            value="Cell value = % of cohort active in month N. Healthy e-commerce = 5–15% at M1. Olist = 0.2–0.7%."
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B3:O3")

    rows = read_csv("cohort_retention.csv")
    months = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
    header_row(ws, 5, ["Cohort"] + months, start_col=2)
    set_col_widths(ws, {"A": 2, "B": 12} | {get_column_letter(i): 8 for i in range(3, 16)})

    for i, row in enumerate(rows):
        r = 6 + i
        ws.cell(row=r, column=2, value=row["cohort_month"]).font = font(bold=True)
        ws.cell(row=r, column=2).fill = fill(LIGHT_GRAY)
        ws.cell(row=r, column=2).border = BORDER
        for j, m in enumerate(months):
            v = row.get(m, "")
            cell = ws.cell(row=r, column=3 + j)
            if v:
                cell.value = float(v) / 100  # convert to fraction so % format works
                cell.number_format = "0.0%"
            cell.alignment = center()
            cell.border = BORDER
            cell.font = font(size=9)

    last_row = 5 + len(rows)
    # Conditional formatting: 3-color scale (red high warning -> green low retention is bad here, so flip)
    # Actually: M0 = 100%, others should be low; we want the eye to see "all red/yellow = bad"
    # Use white-yellow-red where higher = redder (because M0 100% = expected, M1+ should be near 0)
    # Better: skip M0 column, scale only M1-M12
    rule = ColorScaleRule(
        start_type="num", start_value=0, start_color="FFFFFF",
        mid_type="num", mid_value=0.05, mid_color=ACCENT_YELLOW,
        end_type="num", end_value=0.10, end_color=ORANGE,
    )
    ws.conditional_formatting.add(f"D6:O{last_row}", rule)

    # Insights below
    ir = last_row + 3
    ws.cell(row=ir, column=2, value="KEY READINGS").font = font(size=12, bold=True, color=NAVY)
    insights = [
        "M0 = 100% by definition (everyone bought in their cohort month)",
        "M1 = 0.2–0.7% across nearly all cohorts → 99%+ never come back next month",
        "Mature e-commerce benchmark: M1 ≈ 5–15%. Olist is 1–2 orders of magnitude below",
        "93,358 unique customers → only 1,693 (1.81%) bought in more than one month",
        "Implication: this is not a 'low retention' problem — retention essentially does not exist as a behavior",
        "Hypotheses for v2: (a) Brazil-wide e-comm pattern? (b) Product mix skewed to one-time durables? (c) No loyalty program?",
    ]
    for i, t in enumerate(insights):
        ws.cell(row=ir + 1 + i, column=2, value=f"• {t}").font = font()
        ws.merge_cells(start_row=ir + 1 + i, start_column=2, end_row=ir + 1 + i, end_column=15)


# ============================================================================
# Sheet 7 — ROI Calculator (LIVE FORMULAS — the killer feature)
# ============================================================================
def build_roi(wb: Workbook) -> None:
    ws = wb.create_sheet("7. ROI Calculator")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 32, "C": 18, "D": 18, "E": 18, "F": 18, "G": 18, "H": 2})

    ws.cell(row=2, column=2, value="🎯 At-Risk Win-back ROI Calculator").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:G2")
    ws.cell(row=3, column=2,
            value="Edit the YELLOW cells. All scenario columns recompute live."
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B3:G3")

    # ----- Input block (yellow editable cells) -----
    section_title(ws, 5, "INPUTS — edit me", span=7)
    inputs = [
        ("At-risk customers (segment size)", 21975, "#,##0", "From RFM analysis"),
        ("Avg ARPU per customer (R$)", 213, "0", "Historical average for At-Risk segment"),
        ("Repeat-spend rate (% of ARPU on win-back order)", 0.50, "0%", "Conservative: assumes win-back order = 50% of historical average"),
        ("Total CRM cost (R$)", 50000, "#,##0", "Email + discount voucher budget"),
    ]
    header_row(ws, 6, ["Parameter", "Value", "Format", "Notes"], start_col=2)
    for i, (label, val, fmt, note) in enumerate(inputs):
        r = 7 + i
        ws.cell(row=r, column=2, value=label).font = font(bold=True)
        c = ws.cell(row=r, column=3, value=val)
        c.fill = fill(ACCENT_YELLOW)
        c.font = font(bold=True, size=12)
        c.alignment = center()
        c.number_format = fmt
        c.border = Border(left=Side(style="medium", color=ORANGE),
                          right=Side(style="medium", color=ORANGE),
                          top=Side(style="medium", color=ORANGE),
                          bottom=Side(style="medium", color=ORANGE))
        ws.cell(row=r, column=4, value=fmt).font = font(italic=True, size=9, color=DARK_GRAY)
        ws.cell(row=r, column=5, value=note).font = font(italic=True, size=9, color=DARK_GRAY)
        for col in (2, 4, 5):
            ws.cell(row=r, column=col).border = BORDER

    # Cell refs:
    # C7 = at-risk count, C8 = ARPU, C9 = repeat_spend_pct, C10 = cost

    # ----- Scenarios block -----
    section_title(ws, 13, "SCENARIO OUTPUTS — recomputes live", span=7)

    header_row(ws, 14, ["Metric", "Conservative (5%)", "Optimistic (10%)", "Aggressive (20%)", "Custom"], start_col=2)

    # Scenario recall rates (yellow, editable)
    scenarios = [("D", 0.05), ("E", 0.10), ("F", 0.20), ("G", 0.10)]
    ws.cell(row=15, column=2, value="Recall rate (%)").font = font(bold=True)
    for col_letter, default in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        c = ws.cell(row=15, column=col_idx, value=default)
        c.fill = fill(ACCENT_YELLOW if col_letter == "G" else LIGHT_GRAY)
        c.number_format = "0%"
        c.alignment = center()
        c.font = font(bold=True)
        c.border = BORDER

    # Recalled customers = at_risk * recall_rate
    ws.cell(row=16, column=2, value="Recalled customers").font = font(bold=True)
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=16, column=col_idx, value=f"=$C$7*{col_letter}15")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # Incremental revenue = recalled * ARPU * repeat_spend_pct
    ws.cell(row=17, column=2, value="Incremental revenue (R$)").font = font(bold=True)
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=17, column=col_idx, value=f"=$C$7*{col_letter}15*$C$8*$C$9")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # Cost = total cost (constant)
    ws.cell(row=18, column=2, value="CRM cost (R$)").font = font(bold=True)
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=18, column=col_idx, value="=$C$10")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # Net = revenue - cost
    ws.cell(row=19, column=2, value="Net contribution (R$)").font = font(bold=True)
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=19, column=col_idx, value=f"={col_letter}17-{col_letter}18")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER
        cell.font = font(bold=True)

    # ROI = revenue / cost
    ws.cell(row=20, column=2, value="ROI (×)").font = font(bold=True, color=WHITE)
    ws.cell(row=20, column=2).fill = fill(NAVY)
    ws.cell(row=20, column=2).border = BORDER
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=20, column=col_idx, value=f"={col_letter}17/{col_letter}18")
        cell.number_format = "0.0\"×\""
        cell.alignment = center()
        cell.font = font(bold=True, size=14, color=WHITE)
        cell.fill = fill(TEAL)
        cell.border = BORDER

    # Border / formatting clean up on output rows
    for r in (15, 16, 17, 18, 19):
        ws.cell(row=r, column=2).border = BORDER

    # Formula explanation
    ws.cell(row=22, column=2, value="FORMULA").font = font(size=12, bold=True, color=NAVY)
    ws.cell(row=23, column=2, value="Incremental revenue  =  At-risk × Recall rate × ARPU × Repeat-spend %").font = font(italic=True)
    ws.merge_cells("B23:G23")
    ws.cell(row=24, column=2, value="ROI                     =  Incremental revenue ÷ CRM cost").font = font(italic=True)
    ws.merge_cells("B24:G24")

    # Action priority
    ws.cell(row=26, column=2, value="ACTION PRIORITY").font = font(size=12, bold=True, color=NAVY)
    actions = [
        "1. Wave 1: personalized EDM by historical category to all 21,975 at-risk customers (~R$ 50K)",
        "2. Track funnel: open → click → conversion → incremental revenue vs. holdout",
        "3. If recall rate > 8%: 2× budget, add SMS + retargeting touchpoints",
        "4. If recall rate < 3%: switch lever from discount to free shipping (esp. for remote states)",
    ]
    for i, t in enumerate(actions):
        ws.cell(row=27 + i, column=2, value=t).font = font()
        ws.merge_cells(start_row=27 + i, start_column=2, end_row=27 + i, end_column=7)


# ============================================================================
# Sheet 8 — Installments Insight
# ============================================================================
def build_installments(wb: Workbook) -> None:
    ws = wb.create_sheet("8. Installments")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 18, "C": 14, "D": 18, "E": 14, "F": 18, "G": 2})

    ws.cell(row=2, column=2, value="Brazil's Installment Culture — The Hidden CRM Lever").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:F2")
    ws.cell(row=3, column=2,
            value="Brazil-specific differentiator: 73.9% of orders use credit_card, avg 3.5 installments. Two questions: does longer financing → higher AOV? → higher repeat?"
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B3:F3")

    rows = read_csv("installments.csv")
    bucket_en = {
        "1 (一次付清)": "1 (single)",
        "2-3 期": "2–3 installments",
        "4-6 期": "4–6 installments",
        "7-10 期": "7–10 installments",
        "11+ 期": "11+ installments",
    }
    header_row(ws, 5, ["Installment bucket", "Orders", "Avg ticket (R$)", "Customers", "Repeat rate %"], start_col=2)
    for i, row in enumerate(rows):
        r = 6 + i
        ws.cell(row=r, column=2, value=bucket_en[row["bucket"]])
        ws.cell(row=r, column=3, value=int(row["orders"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=float(row["avg_ticket"])).number_format = "0"
        ws.cell(row=r, column=5, value=int(row["customers"])).number_format = "#,##0"
        ws.cell(row=r, column=6, value=float(row["repeat_rate_pct"]) / 100).number_format = "0.00%"
        for col in range(2, 7):
            ws.cell(row=r, column=col).border = BORDER

    # AOV chart
    bar = BarChart()
    bar.type = "col"
    bar.style = 12
    bar.title = "Avg ticket (R$) by installment bucket — 7-10 installments = 3.48× single-payment"
    bar.y_axis.title = "Avg ticket (R$)"
    bar.x_axis.title = "Installments"
    bar.height = 9
    bar.width = 18
    data = Reference(ws, min_col=4, min_row=5, max_row=5 + len(rows), max_col=4)
    cats = Reference(ws, min_col=2, min_row=6, max_row=5 + len(rows))
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    ws.add_chart(bar, "B14")

    # Repeat rate chart
    bar2 = BarChart()
    bar2.type = "col"
    bar2.style = 13
    bar2.title = "Repeat rate by installment bucket — 7+ installments customers retain 65% better"
    bar2.y_axis.title = "Repeat rate"
    bar2.x_axis.title = "Installments"
    bar2.height = 9
    bar2.width = 18
    data2 = Reference(ws, min_col=6, min_row=5, max_row=5 + len(rows), max_col=6)
    bar2.add_data(data2, titles_from_data=True)
    bar2.set_categories(cats)
    ws.add_chart(bar2, "B33")

    ws.cell(row=53, column=2, value="TWO FINDINGS & LEVERS").font = font(size=12, bold=True, color=NAVY)
    findings = [
        "Revenue lever — 7–10 installments AOV is 3.48× single payment (R$ 334 vs R$ 96). Linear, no inversion.",
        "Retention lever — 7–10 installment customers repeat 65% more often (4.13% vs 2.51%). They're the rare customers who do come back.",
        "Why? Multi-month installment ledger keeps customers transactionally engaged with Olist → installments = invisible CRM.",
        "Action 1: promote 7+ installment plans on home + checkout (currently only 15% of credit-card orders).",
        "Action 2: send 'no-interest installment' EDM to single-payment customers on second visit.",
        "Action 3: negotiate longer interest-free terms with issuers (8 months is sweet spot, n=4,268; test 12).",
        "Caveat: causality not proven — could be 'high ticket → must installment'. A/B test installment availability on same SKU page.",
    ]
    for i, t in enumerate(findings):
        ws.cell(row=54 + i, column=2, value=f"• {t}").font = font()
        ws.merge_cells(start_row=54 + i, start_column=2, end_row=54 + i, end_column=6)


# ============================================================================
# Sheet 9 — Logistics
# ============================================================================
def build_logistics(wb: Workbook) -> None:
    ws = wb.create_sheet("9. Logistics")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 12, "C": 18, "D": 18, "E": 18, "F": 2})

    ws.cell(row=2, column=2, value="Logistics — Estimated vs Actual Delivery (by State)").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:E2")
    ws.cell(row=3, column=2,
            value="National avg actual = 15.4 days. ETA avg = 24 days. Platform under-promises by 36% — opportunity to tighten ETA messaging."
            ).font = font(italic=True, color=DARK_GRAY)
    ws.merge_cells("B3:E3")

    rows = read_csv("logistics.csv")
    header_row(ws, 5, ["State", "Actual days", "Estimated days", "ETA gap (days)"], start_col=2)
    for i, row in enumerate(rows):
        r = 6 + i
        actual = float(row["實際天數"])
        eta = float(row["預期天數"])
        ws.cell(row=r, column=2, value=row["州"]).font = font(bold=True)
        ws.cell(row=r, column=3, value=actual).number_format = "0.0"
        ws.cell(row=r, column=4, value=eta).number_format = "0.0"
        ws.cell(row=r, column=5, value=eta - actual).number_format = "0.0"
        for col in range(2, 6):
            ws.cell(row=r, column=col).border = BORDER

    chart = BarChart()
    chart.type = "bar"
    chart.style = 12
    chart.title = "Actual vs Estimated delivery days — SP best (8.8d), RN worst (19.3d)"
    chart.height = 14
    chart.width = 22
    data = Reference(ws, min_col=3, min_row=5, max_row=5 + len(rows), max_col=4)
    cats = Reference(ws, min_col=2, min_row=6, max_row=5 + len(rows))
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "G5")

    ws.cell(row=23, column=2, value="LOGISTICS INSIGHTS").font = font(size=12, bold=True, color=NAVY)
    insights = [
        "SP (8.8d) vs RN (19.3d) = 2.2× state-level gap. Replicate SP fulfillment model in high-order states.",
        "Platform-wide ETA is conservative by 36%. Marketing pages can show tighter promises → conversion lift.",
        "Cross-analyze 1-star reviews with delivery delay > ETA to quantify NPS impact.",
        "Remote states need free-shipping levers (per ROI sheet's 'switch to free shipping' branch).",
    ]
    for i, t in enumerate(insights):
        ws.cell(row=24 + i, column=2, value=f"• {t}").font = font()
        ws.merge_cells(start_row=24 + i, start_column=2, end_row=24 + i, end_column=5)


# ============================================================================
# Sheet 10 — Methodology & Tech Stack
# ============================================================================
def build_methodology(wb: Workbook) -> None:
    ws = wb.create_sheet("10. Methodology")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 24, "C": 60, "D": 2})

    ws.cell(row=2, column=2, value="Methodology & Tech Stack").font = font(size=18, bold=True, color=NAVY)
    ws.merge_cells("B2:C2")

    section_title(ws, 4, "Tech stack & why", span=4)
    stack = [
        ("Python 3.12", "Glue language for ETL + analysis"),
        ("SQLite + SQL", "9-table schema; SQL Window Functions for RFM (NTILE)"),
        ("pandas", "Cohort matrix + installment bucketing"),
        ("matplotlib", "Static portfolio charts (cohort, installments)"),
        ("Streamlit", "Interactive 5-page dashboard with ROI calculator"),
        ("Tableau Public", "Stakeholder-facing dashboard"),
        ("openpyxl", "This Excel portfolio (live formulas + conditional formatting)"),
    ]
    header_row(ws, 5, ["Tool", "Role"], start_col=2)
    for i, (k, v) in enumerate(stack):
        r = 6 + i
        ws.cell(row=r, column=2, value=k).font = font(bold=True)
        ws.cell(row=r, column=3, value=v).alignment = left()
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=3).border = BORDER

    section_title(ws, 14, "Core SQL — RFM with NTILE Window Function", span=4)
    sql = (
        "WITH snapshot AS (\n"
        "    SELECT MAX(order_purchase_timestamp) AS snapshot_date\n"
        "    FROM orders WHERE order_status = 'delivered'\n"
        "),\n"
        "rfm_base AS (\n"
        "    SELECT c.customer_unique_id,\n"
        "           ROUND(JULIANDAY((SELECT snapshot_date FROM snapshot))\n"
        "                 - JULIANDAY(MAX(o.order_purchase_timestamp)), 0) AS recency_days,\n"
        "           COUNT(DISTINCT o.order_id) AS frequency,\n"
        "           ROUND(SUM(oi.price), 2)    AS monetary\n"
        "    FROM orders o\n"
        "    JOIN order_items oi ON o.order_id = oi.order_id\n"
        "    JOIN customers   c  ON o.customer_id = c.customer_id\n"
        "    WHERE o.order_status = 'delivered'\n"
        "    GROUP BY c.customer_unique_id\n"
        "),\n"
        "rfm_scored AS (\n"
        "    SELECT *,\n"
        "        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,\n"
        "        NTILE(5) OVER (ORDER BY frequency    ASC ) AS f_score,\n"
        "        NTILE(5) OVER (ORDER BY monetary     ASC ) AS m_score\n"
        "    FROM rfm_base\n"
        ")\n"
        "SELECT CASE\n"
        "    WHEN r_score>=4 AND f_score>=4 AND m_score>=4 THEN 'Champions'\n"
        "    WHEN r_score>=4 AND f_score>=3                THEN 'Loyal'\n"
        "    WHEN r_score>=4                               THEN 'Potential New'\n"
        "    WHEN r_score<=2 AND f_score>=3                THEN 'At Risk'\n"
        "    WHEN r_score<=2                               THEN 'Lost'\n"
        "    ELSE                                                'Average'\n"
        "END AS segment, COUNT(*) AS customers, ROUND(AVG(monetary),2) AS arpu,\n"
        "  ROUND(SUM(monetary),2) AS revenue\n"
        "FROM rfm_scored GROUP BY segment ORDER BY revenue DESC;"
    )
    sc = ws.cell(row=15, column=2, value=sql)
    sc.font = Font(name="Consolas", size=9)
    sc.alignment = Alignment(wrap_text=True, vertical="top")
    sc.fill = fill(LIGHT_GRAY)
    sc.border = BORDER
    ws.merge_cells("B15:C15")
    ws.row_dimensions[15].height = 380

    section_title(ws, 17, "Why NTILE (SQL) over pandas qcut", span=4)
    table = [
        ("Portability", "Snowflake / BigQuery / Redshift / SQLite all run identical SQL", "Python only"),
        ("Scale", "Runs in DB — handles tens of millions of rows", "Pulls all rows into Python memory"),
        ("Orchestration", "Slots into dbt / Airflow", "Needs custom wrapper"),
        ("Hiring signal", "'Knows the warehouse' = senior signal", "'Knows pandas' = junior signal"),
    ]
    header_row(ws, 18, ["Dimension", "NTILE (SQL)", "pandas qcut"], start_col=2)
    # Set the column count to 3 for this table
    set_col_widths(ws, {"D": 30})
    for i, (dim, a, b) in enumerate(table):
        r = 19 + i
        ws.cell(row=r, column=2, value=dim).font = font(bold=True)
        ws.cell(row=r, column=3, value=a).alignment = left()
        ws.cell(row=r, column=4, value=b).alignment = left()
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = BORDER

    section_title(ws, 24, "Caveats & next steps (honest disclosure)", span=4)
    caveats = [
        "F dimension has near-zero variance — segmentation is effectively R × M. Acknowledged in v1.",
        "'Loyal' segment ARPU is low (R$ 89) because the rule sets R≥4, F≥3 without M floor — v2 adds M condition.",
        "2018 data truncated at 2018-10. Apparent post-Sep dip is data cutoff, not real decline.",
        "Causality between installments → AOV not established — needs A/B test on identical SKU pages.",
        "Next: review-score vs. delivery-delay correlation (Pearson/Spearman); Prophet/ARIMA forecast on monthly GMV.",
    ]
    for i, t in enumerate(caveats):
        ws.cell(row=25 + i, column=2, value=f"• {t}").font = font()
        ws.merge_cells(start_row=25 + i, start_column=2, end_row=25 + i, end_column=4)


# ============================================================================
# Build
# ============================================================================
def main() -> None:
    wb = Workbook()
    # Remove default sheet
    default = wb.active
    wb.remove(default)

    build_cover(wb)
    build_summary(wb)
    build_kpis(wb)
    build_revenue(wb)
    build_rfm(wb)
    build_cohort(wb)
    build_roi(wb)
    build_installments(wb)
    build_logistics(wb)
    build_methodology(wb)

    # Set Cover as the active sheet
    wb.active = 0
    wb.save(XLSX_PATH)
    print(f"Wrote {XLSX_PATH} ({XLSX_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

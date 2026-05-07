"""Generate output/portfolio.xlsx — 13-sheet industry-standard Excel portfolio.

Sheet layout (12 visible + 1 hidden):
  01_Cover, 02_TOC, 03_Data_Dictionary
  04_Executive_Summary
  05_KPI_Dashboard, 06_Revenue_Trend, 07_RFM_Segments, 08_Cohort_Heatmap
  09_ROI_Calculator (live formulas)
  10_Installments, 11_Logistics
  12_Methodology
  + hidden helper: _data_calc (central data hub; visible sheets pull values from here)

Industry conventions applied:
  - Excel Tables (ListObject) on every tabular block
  - Center Across Selection (centerContinuous) replaces merged cells for headers
  - Frozen panes on every data sheet
  - Conditional formatting (data bars / icon sets / color scale)
  - Named ranges for ROI inputs
  - Visible sheets reference _data_calc via formulas (XLOOKUP / direct ref)
  - No emoji; semantics conveyed via icon-set conditional formatting
"""
from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import (
    ColorScaleRule, DataBarRule, IconSetRule,
)
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DATA_DIR = ROOT / "data"
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


def center_across() -> Alignment:
    """Center Across Selection — visual centering without merging (industry preferred)."""
    return Alignment(horizontal="centerContinuous", vertical="center", wrap_text=True)


def header_row(ws: Worksheet, row: int, cols: list[str], start_col: int = 2) -> None:
    for i, label in enumerate(cols):
        c = ws.cell(row=row, column=start_col + i, value=label)
        c.font = font(bold=True, color=WHITE)
        c.fill = fill(NAVY)
        c.alignment = center()
        c.border = BORDER


def title_block(ws: Worksheet, row: int, title: str, subtitle: str = "",
                start_col: int = 2, span: int = 5) -> None:
    """Main title at column B (industry margin convention), no merged cells."""
    end_col = start_col + span - 1
    c = ws.cell(row=row, column=start_col, value=title)
    c.font = font(size=18, bold=True, color=NAVY)
    c.alignment = center_across()
    for col in range(start_col + 1, end_col + 1):
        ws.cell(row=row, column=col).alignment = center_across()
    if subtitle:
        c2 = ws.cell(row=row + 1, column=start_col, value=subtitle)
        c2.font = font(size=11, italic=True, color=DARK_GRAY)
        c2.alignment = center_across()
        for col in range(start_col + 1, end_col + 1):
            ws.cell(row=row + 1, column=col).alignment = center_across()


def section_header(ws: Worksheet, row: int, text: str, start_col: int = 2) -> None:
    """Section header — always column B for vertical alignment with main title."""
    c = ws.cell(row=row, column=start_col, value=text)
    c.font = font(size=13, bold=True, color=NAVY)


def add_table(ws: Worksheet, ref: str, name: str, style: str = "TableStyleMedium2") -> None:
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name=style, showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(tbl)


def add_named_range(wb: Workbook, name: str, sheet: str, ref: str) -> None:
    wb.defined_names.append(DefinedName(name=name, attr_text=f"'{sheet}'!{ref}"))


def set_col_widths(ws: Worksheet, widths: dict[str, float]) -> None:
    for col, w in widths.items():
        ws.column_dimensions[col].width = w


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUTPUT_DIR / name).open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_raw_sample(filename: str, n: int = 10) -> tuple[list[str], list[list[str]]]:
    """Read first N rows of a raw data CSV. Returns (headers, rows)."""
    path = DATA_DIR / filename
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows: list[list[str]] = []
        for i, row in enumerate(reader):
            if i >= n:
                break
            rows.append(row)
    return headers, rows


def count_csv_rows(filename: str) -> int:
    path = DATA_DIR / filename
    with path.open(encoding="utf-8-sig") as f:
        return sum(1 for _ in f) - 1  # exclude header


def aggregate_state_payment() -> tuple[list[str], list[str], dict[tuple[str, str], int]]:
    """Compute state × payment_type order count from raw CSVs.
    Returns (sorted_states, payment_types, dict[(state, ptype)] = count)."""
    from collections import defaultdict
    cust_state: dict[str, str] = {}
    with (DATA_DIR / "olist_customers_dataset.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cust_state[row["customer_id"]] = row["customer_state"]

    order_state: dict[str, str] = {}
    with (DATA_DIR / "olist_orders_dataset.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            order_state[row["order_id"]] = cust_state.get(row["customer_id"], "")

    pivot: dict[tuple[str, str], int] = defaultdict(int)
    payment_types: set[str] = set()
    # Collapse duplicate payment lines: count each (state, ptype, order_id) at most once
    seen_per_combo: dict[tuple[str, str], set[str]] = defaultdict(set)
    with (DATA_DIR / "olist_order_payments_dataset.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            state = order_state.get(row["order_id"], "")
            ptype = row["payment_type"]
            if not state or not ptype or ptype == "not_defined":
                continue
            payment_types.add(ptype)
            combo = (state, ptype)
            if row["order_id"] not in seen_per_combo[combo]:
                pivot[combo] += 1
                seen_per_combo[combo].add(row["order_id"])

    # Sort states by total volume descending
    state_totals: dict[str, int] = defaultdict(int)
    for (s, _p), v in pivot.items():
        state_totals[s] += v
    states_sorted = sorted(state_totals.keys(), key=lambda s: state_totals[s], reverse=True)
    payment_sorted = sorted(payment_types, key=lambda p: -sum(pivot[(s, p)] for s in states_sorted))
    return states_sorted, payment_sorted, dict(pivot)


def read_category_translation() -> list[tuple[str, str]]:
    """Read PT→EN category translation. Returns list of (pt, en) tuples."""
    path = DATA_DIR / "product_category_name_translation.csv"
    out: list[tuple[str, str]] = []
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            out.append((row["product_category_name"], row["product_category_name_english"]))
    return out


# ============================================================================
# Hidden helper: _data_calc — central data hub
# ============================================================================
def build_data_calc(wb: Workbook) -> dict[str, int | str]:
    """Build the hidden _data_calc sheet. Returns row pointers so visible
    sheets can build cross-sheet formulas like =_data_calc!B5."""
    ws = wb.create_sheet("_data_calc")
    ws.sheet_state = "hidden"
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 32, "B": 16, "C": 14, "D": 16, "E": 16, "F": 16,
                        "G": 14, "H": 14, "I": 12, "J": 10, "K": 10, "L": 10,
                        "M": 10, "N": 10, "O": 10, "P": 10})

    refs: dict[str, int | str] = {}

    # ---- Section 1: KPI Lookup ----
    ws.cell(row=1, column=1, value="KPI Lookup").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, 2, ["Metric", "Value", "Format"], start_col=1)
    kpi_pairs = [
        ("Total orders", 99441, "#,##0"),
        ("Unique customers", 96096, "#,##0"),
        ("Sellers", 3095, "#,##0"),
        ("Products", 32951, "#,##0"),
        ("Product categories", 71, "#,##0"),
        ("States covered", 27, "0"),
        ("Cities covered", 4119, "#,##0"),
        ("Total GMV (R$)", 13591644.0, "#,##0"),
        ("AOV (R$)", 137.41, "0.00"),
        ("Cross-month repeat rate", 0.0181, "0.00%"),
        ("Champions ARPU (R$)", 274.0, "0"),
        ("At-Risk customers", 21975, "#,##0"),
        ("At-Risk ARPU (R$)", 213.0, "0"),
        ("Avg actual delivery (days)", 15.4, "0.0"),
        ("Avg ETA (days)", 24.0, "0.0"),
        ("Repeat customers (count)", 1693, "#,##0"),
    ]
    for i, (k, v, fmt) in enumerate(kpi_pairs):
        r = 3 + i
        ws.cell(row=r, column=1, value=k)
        c = ws.cell(row=r, column=2, value=v)
        c.number_format = fmt
        ws.cell(row=r, column=3, value=fmt).font = font(italic=True, size=9, color=DARK_GRAY)
    kpi_end = 2 + len(kpi_pairs)
    add_table(ws, f"A2:C{kpi_end}", "tbl_kpi_lookup")
    refs["kpi_start"] = 3
    refs["kpi_end"] = kpi_end

    # ---- Section 2: Yearly KPIs ----
    s2 = kpi_end + 3
    ws.cell(row=s2, column=1, value="Yearly KPIs").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, s2 + 1, ["Year", "GMV (R$ M)", "Orders", "Avg Review", "Avg Delivery (days)"], start_col=1)
    yearly = read_csv("kpi_yearly.csv")
    for i, row in enumerate(yearly):
        r = s2 + 2 + i
        ws.cell(row=r, column=1, value=int(row["年份"]))
        ws.cell(row=r, column=2, value=float(row["總營收_M"]))
        ws.cell(row=r, column=3, value=int(row["總訂單數"]))
        ws.cell(row=r, column=4, value=float(row["平均評分"]))
        ws.cell(row=r, column=5, value=float(row["平均送達天數"]))
    y_end = s2 + 1 + len(yearly)
    add_table(ws, f"A{s2 + 1}:E{y_end}", "tbl_yearly")
    refs["yearly_start"] = s2 + 2
    refs["yearly_end"] = y_end

    # ---- Section 3: Revenue by month ----
    s3 = y_end + 3
    ws.cell(row=s3, column=1, value="Monthly Revenue").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, s3 + 1, ["Month", "Revenue (R$)"], start_col=1)
    rev = read_csv("revenue.csv")
    for i, row in enumerate(rev):
        r = s3 + 2 + i
        ws.cell(row=r, column=1, value=row["月份"])
        ws.cell(row=r, column=2, value=float(row["總營收"]))
    r_end = s3 + 1 + len(rev)
    add_table(ws, f"A{s3 + 1}:B{r_end}", "tbl_revenue")
    refs["rev_start"] = s3 + 2
    refs["rev_end"] = r_end

    # ---- Section 4: RFM ----
    s4 = r_end + 3
    ws.cell(row=s4, column=1, value="RFM Segments").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, s4 + 1, ["Segment", "Customers", "Customer %", "Revenue (R$)", "Revenue %", "ARPU (R$)", "Avg Recency (d)"], start_col=1)
    rfm = read_csv("rfm_segments.csv")
    seg_map = {
        "冠軍客戶": "Champions",
        "流失風險": "At Risk",
        "一般客戶": "Average",
        "忠誠客戶": "Loyal Low-spend",
        "已流失": "Lost",
        "潛力新客": "Potential New",
    }
    priority = ["冠軍客戶", "流失風險", "忠誠客戶", "一般客戶", "潛力新客", "已流失"]
    rfm_sorted = sorted(rfm, key=lambda r: priority.index(r["segment"]))
    for i, row in enumerate(rfm_sorted):
        r = s4 + 2 + i
        ws.cell(row=r, column=1, value=seg_map[row["segment"]])
        ws.cell(row=r, column=2, value=int(row["客戶數"]))
        ws.cell(row=r, column=3, value=float(row["客戶佔比_%"]) / 100)
        ws.cell(row=r, column=4, value=float(row["群組總營收"]))
        ws.cell(row=r, column=5, value=float(row["營收佔比_%"]) / 100)
        ws.cell(row=r, column=6, value=float(row["平均_M_元"]))
        ws.cell(row=r, column=7, value=float(row["平均_R_天"]))
    rfm_end = s4 + 1 + len(rfm_sorted)
    add_table(ws, f"A{s4 + 1}:G{rfm_end}", "tbl_rfm")
    refs["rfm_start"] = s4 + 2
    refs["rfm_end"] = rfm_end

    # ---- Section 5: Installments ----
    s5 = rfm_end + 3
    ws.cell(row=s5, column=1, value="Installments").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, s5 + 1, ["Bucket", "Orders", "Avg Ticket (R$)", "Customers", "Repeat Rate"], start_col=1)
    inst = read_csv("installments.csv")
    bucket_en = {
        "1 (一次付清)": "1 (single)",
        "2-3 期": "2-3 installments",
        "4-6 期": "4-6 installments",
        "7-10 期": "7-10 installments",
        "11+ 期": "11+ installments",
    }
    for i, row in enumerate(inst):
        r = s5 + 2 + i
        ws.cell(row=r, column=1, value=bucket_en[row["bucket"]])
        ws.cell(row=r, column=2, value=int(row["orders"]))
        ws.cell(row=r, column=3, value=float(row["avg_ticket"]))
        ws.cell(row=r, column=4, value=int(row["customers"]))
        ws.cell(row=r, column=5, value=float(row["repeat_rate_pct"]) / 100)
    inst_end = s5 + 1 + len(inst)
    add_table(ws, f"A{s5 + 1}:E{inst_end}", "tbl_installments")
    refs["inst_start"] = s5 + 2
    refs["inst_end"] = inst_end

    # ---- Section 6: Logistics ----
    s6 = inst_end + 3
    ws.cell(row=s6, column=1, value="Logistics by State").font = font(bold=True, size=14, color=NAVY)
    header_row(ws, s6 + 1, ["State", "Actual days", "Estimated days", "ETA gap (days)"], start_col=1)
    log = read_csv("logistics.csv")
    for i, row in enumerate(log):
        r = s6 + 2 + i
        ws.cell(row=r, column=1, value=row["州"])
        actual = float(row["實際天數"])
        eta = float(row["預期天數"])
        ws.cell(row=r, column=2, value=actual)
        ws.cell(row=r, column=3, value=eta)
        ws.cell(row=r, column=4, value=eta - actual)
    log_end = s6 + 1 + len(log)
    add_table(ws, f"A{s6 + 1}:D{log_end}", "tbl_logistics")
    refs["log_start"] = s6 + 2
    refs["log_end"] = log_end

    # ---- Section 7: Cohort matrix ----
    s7 = log_end + 3
    ws.cell(row=s7, column=1, value="Cohort Retention Matrix").font = font(bold=True, size=14, color=NAVY)
    months = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
    header_row(ws, s7 + 1, ["Cohort"] + months, start_col=1)
    cohort = read_csv("cohort_retention.csv")
    for i, row in enumerate(cohort):
        r = s7 + 2 + i
        ws.cell(row=r, column=1, value=row["cohort_month"])
        for j, m in enumerate(months):
            v = row.get(m, "")
            if v:
                ws.cell(row=r, column=2 + j, value=float(v) / 100)
    cohort_end = s7 + 1 + len(cohort)
    last_col = get_column_letter(1 + len(months))
    add_table(ws, f"A{s7 + 1}:{last_col}{cohort_end}", "tbl_cohort")
    refs["cohort_start"] = s7 + 2
    refs["cohort_end"] = cohort_end

    return refs


def kpi_lookup_formula(refs: dict, metric_name: str) -> str:
    """XLOOKUP formula fetching a KPI value from _data_calc by metric name.
    Uses the `_xlfn.` prefix that openpyxl requires for modern Excel functions."""
    range_metric = f"_data_calc!$A$3:$A${refs['kpi_end']}"
    range_value = f"_data_calc!$B$3:$B${refs['kpi_end']}"
    return f'=_xlfn.XLOOKUP("{metric_name}",{range_metric},{range_value})'


# ============================================================================
# 01_Cover
# ============================================================================
def build_cover(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("01_Cover")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 28, "C": 28, "D": 28, "E": 28, "F": 2})

    ws.row_dimensions[2].height = 40
    title = ws.cell(row=2, column=2, value="Olist Brazilian E-Commerce")
    title.font = font(size=26, bold=True, color=NAVY)
    title.alignment = center_across()
    for col in range(3, 6):
        ws.cell(row=2, column=col).alignment = center_across()

    ws.row_dimensions[3].height = 26
    sub = ws.cell(row=3, column=2,
                  value="End-to-End Customer Analytics — SQL · RFM · Cohort · ROI")
    sub.font = font(size=14, italic=True, color=DARK_GRAY)
    sub.alignment = center_across()
    for col in range(3, 6):
        ws.cell(row=3, column=col).alignment = center_across()

    # Author / role / dataset block
    pairs = [
        ("Author", "Jen-Ho Cheng"),
        ("Role", "Data / Product Analyst — E-commerce"),
        ("Dataset", "Olist (Brazil) · 99,441 orders · 2016–2018"),
    ]
    for i, (k, v) in enumerate(pairs):
        ws.cell(row=5 + i, column=2, value=k).font = font(bold=True, color=NAVY)
        ws.cell(row=5 + i, column=3, value=v).font = font()

    # Headline metrics
    section_header(ws, 9, "THREE HEADLINE FINDINGS")
    cards = [
        ("R$ 469K", "Win-back revenue opportunity",
         "21,975 at-risk customers · 9.4× ROI in aggressive scenario"),
        ("1.81%", "Cross-month repeat rate",
         "Platform-level retention failure (vs. 5–15% mature benchmark)"),
        ("3.48×", "ARPU lift from 7-10 installments",
         "R$ 334 vs R$ 96 single payment — Brazil's hidden CRM"),
    ]
    for i, (big, mid, small) in enumerate(cards):
        col = 2 + i
        ws.row_dimensions[11].height = 38
        ws.row_dimensions[12].height = 22
        ws.row_dimensions[13].height = 36
        for r, val, sz in [(11, big, 24), (12, mid, 11)]:
            c = ws.cell(row=r, column=col, value=val)
            c.font = font(size=sz, bold=True, color=WHITE)
            c.fill = fill([NAVY, TEAL, ORANGE][i])
            c.alignment = center()
            c.border = BORDER
        c3 = ws.cell(row=13, column=col, value=small)
        c3.font = font(size=9)
        c3.fill = fill(LIGHT_GRAY)
        c3.alignment = center()
        c3.border = BORDER

    # Live links
    section_header(ws, 16, "LIVE LINKS")
    links = [
        ("Streamlit App", "https://olist-jenho.streamlit.app/",
         "Interactive 5-page dashboard with ROI calculator"),
        ("HTML Dashboard", "https://kengkeng44.github.io/olist-project/",
         "Static GitHub Pages site"),
        ("Tableau Public",
         "https://public.tableau.com/app/profile/jenho.cheng/viz/2_17739060990590/1?publish=yes",
         "Tableau visualization"),
        ("GitHub Repo", "https://github.com/kengkeng44/olist-project",
         "Full source code + Notebook + SQL"),
        ("Pitch Deck (PDF)",
         "https://github.com/kengkeng44/olist-project/blob/master/slides/portfolio.pdf",
         "13-slide PM-style deck"),
    ]
    header_row(ws, 17, ["Resource", "URL", "What you'll find"])
    for i, (label, url, desc) in enumerate(links):
        r = 18 + i
        ws.cell(row=r, column=2, value=label).font = font(bold=True)
        c = ws.cell(row=r, column=3, value=url)
        c.hyperlink = url
        c.font = font(color="0563C1")
        c.alignment = left()
        ws.cell(row=r, column=4, value=desc).alignment = left()
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = BORDER

    # Tech stack chips
    section_header(ws, 25, "TECH STACK")
    stack = ["Python", "SQLite", "SQL (NTILE Window)", "pandas", "matplotlib", "Streamlit", "Tableau"]
    for i, t in enumerate(stack):
        c = ws.cell(row=26 + i // 4, column=2 + i % 4, value=t)
        c.font = font(bold=True, color=NAVY)
        c.fill = fill(ACCENT_YELLOW)
        c.alignment = center()
        c.border = BORDER


# ============================================================================
# 02_TOC
# ============================================================================
def build_toc(wb: Workbook) -> None:
    ws = wb.create_sheet("02_TOC")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 6, "C": 30, "D": 56, "E": 2})

    title_block(ws, 2, "Table of Contents", span=4)

    header_row(ws, 5, ["#", "Sheet", "What it shows"])
    entries = [
        ("01", "01_Cover", "Headline metrics + live links to all artifacts"),
        ("02", "02_TOC", "This page"),
        ("03", "03_Data_Dictionary", "9-table schema + 3-row sample of the 5 most-joined tables"),
        ("04", "04_Executive_Summary", "60-second brief: question → method → 3 findings → recommendation"),
        ("05", "05_KPI_Dashboard", "Scale, yearly KPIs, status mix, payment mix (formulas → _data_calc)"),
        ("06", "06_Revenue_Trend", "Monthly revenue + line chart (Excel Table)"),
        ("07", "07_RFM_Segments", "RFM with NTILE; Pareto + Champions/At-Risk priority (icon set)"),
        ("08", "08_Cohort_Heatmap", "13-month retention matrix with color scale + frozen pane"),
        ("09", "09_ROI_Calculator", "Live formulas — recall rate slider, scenarios, Named Range inputs"),
        ("10", "10_Installments", "Brazil installment culture — AOV/repeat rate by bucket"),
        ("11", "11_Logistics", "State-level ETA gap with 3-color conditional formatting"),
        ("12", "12_Methodology", "Tech stack, core SQL, NTILE-vs-pandas, caveats, upgrade path"),
        ("13", "13_Pivot_Analysis", "VLOOKUP / INDEX-MATCH / XLOOKUP side-by-side + SUMIFS pivot (state × payment)"),
    ]
    for i, (num, sheet, desc) in enumerate(entries):
        r = 6 + i
        ws.cell(row=r, column=2, value=num).alignment = center()
        c = ws.cell(row=r, column=3, value=sheet)
        c.font = font(bold=True, color="0563C1")
        c.hyperlink = f"#'{sheet}'!A1"
        c.alignment = left()
        ws.cell(row=r, column=4, value=desc).alignment = left()
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = BORDER

    ws.freeze_panes = "B6"


# ============================================================================
# 03_Data_Dictionary
# ============================================================================
def build_data_dictionary(wb: Workbook) -> None:
    ws = wb.create_sheet("03_Data_Dictionary")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 26, "C": 14, "D": 44, "E": 2})

    title_block(ws, 2, "Data Dictionary",
                "9 tables · 1.55M rows. 3-row samples below.",
                span=4)

    # Schema overview — one-line descriptions only
    section_header(ws, 5, "9 source tables")
    header_row(ws, 6, ["Table", "Rows", "What's in it"])
    schema = [
        ("olist_orders_dataset", "olist_orders_dataset.csv",
         "Order header + 8 timestamps (purchase → delivery)."),
        ("olist_customers_dataset", "olist_customers_dataset.csv",
         "customer_id (per order) + customer_unique_id + ZIP."),
        ("olist_order_items_dataset", "olist_order_items_dataset.csv",
         "Line items: 1 row per (order, product, seller) with price + freight."),
        ("olist_order_payments_dataset", "olist_order_payments_dataset.csv",
         "Payment type (boleto / credit_card / voucher / debit_card) + installments."),
        ("olist_order_reviews_dataset", "olist_order_reviews_dataset.csv",
         "1-5 star reviews + comment text."),
        ("olist_products_dataset", "olist_products_dataset.csv",
         "Product attributes (category, weight, dimensions)."),
        ("olist_sellers_dataset", "olist_sellers_dataset.csv",
         "Seller ZIP + state."),
        ("olist_geolocation_dataset", "olist_geolocation_dataset.csv",
         "ZIP-level lat/lng (state-level aggregations only)."),
        ("product_category_name_translation", "product_category_name_translation.csv",
         "PT->EN mapping for the 71 product categories."),
    ]
    for i, (name, fname, desc) in enumerate(schema):
        r = 7 + i
        rows = count_csv_rows(fname)
        ws.cell(row=r, column=2, value=name).font = Font(name="Consolas", size=10, bold=True)
        ws.cell(row=r, column=3, value=rows).number_format = "#,##0"
        ws.cell(row=r, column=4, value=desc).alignment = left()
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = BORDER
    schema_end = 6 + len(schema)
    add_table(ws, f"B6:D{schema_end}", "tbl_schema")

    # Sample blocks — 3 rows each, the 5 most-joined tables
    sample_files = [
        ("orders", "olist_orders_dataset.csv"),
        ("customers", "olist_customers_dataset.csv"),
        ("items", "olist_order_items_dataset.csv"),
        ("payments", "olist_order_payments_dataset.csv"),
        ("reviews", "olist_order_reviews_dataset.csv"),
    ]
    cur_row = schema_end + 3
    for short, filename in sample_files:
        section_header(ws, cur_row, f"{filename} — first 3 rows")
        cur_row += 1
        headers, rows = read_raw_sample(filename, n=3)
        for i, _ in enumerate(headers):
            col = 2 + i
            ws.column_dimensions[get_column_letter(col)].width = max(
                14, ws.column_dimensions[get_column_letter(col)].width or 0
            )
        header_row(ws, cur_row, headers)
        for ri, row in enumerate(rows):
            r = cur_row + 1 + ri
            for ci, val in enumerate(row):
                cell = ws.cell(row=r, column=2 + ci, value=val)
                cell.font = Font(name="Consolas", size=9)
                cell.border = BORDER
                cell.alignment = left()
        sample_end = cur_row + len(rows)
        last_col = get_column_letter(1 + len(headers))
        add_table(ws, f"B{cur_row}:{last_col}{sample_end}", f"tbl_sample_{short}")
        cur_row = sample_end + 2

    ws.freeze_panes = "B7"


# ============================================================================
# 04_Executive_Summary
# ============================================================================
def build_summary(wb: Workbook) -> None:
    ws = wb.create_sheet("04_Executive_Summary")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 18, "C": 60, "D": 2})

    title_block(ws, 2, "Executive Summary", span=2)

    blocks = [
        ("Question",
         "Brazil's largest SMB marketplace (Olist, 12,000+ sellers) released 99K orders 2016–2018. "
         "Where can the platform unlock the biggest revenue lever next quarter?"),
        ("Method",
         "9-table SQLite schema · SQL Window Functions (NTILE) for RFM scoring · Cohort retention · "
         "Installment-bucket analysis · Quantified ROI scenarios."),
        ("Finding 1 — Pareto",
         "Champions (16% of customers) + At-Risk (24%) drive 67% of revenue. Marketing spend should "
         "consolidate here, not chase the long tail."),
        ("Finding 2 — Retention crisis",
         "Cross-month repeat rate is 1.81%. Cohort heatmap shows M1 at 0.2–0.7%. Olist is "
         "acquisition-driven, not retention-driven — biggest leverage is win-back, not new acquisition."),
        ("Finding 3 — Installments = hidden CRM",
         "Customers paying in 7–10 installments have 3.48× ARPU and 65% higher repeat rate than "
         "single-payment buyers. Installment plans are an under-leveraged retention mechanism."),
        ("Recommendation",
         "Launch personalized win-back EDM to 21,975 At-Risk customers (cost ≈ R$ 50K). Conservative "
         "5% recall = R$ 117K incremental revenue (2.3× ROI). Aggressive 20% = R$ 469K (9.4× ROI)."),
        ("Decision artifact",
         "PRD-style proposal in proposals/recall_campaign_prd.md — includes timeline, cross-team RACI, "
         "A/B design, kill criteria. See sheet 09_ROI_Calculator for the live ROI calculator."),
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
# 05_KPI_Dashboard — formulas reference _data_calc
# ============================================================================
def build_kpis(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("05_KPI_Dashboard")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 32, "C": 18, "D": 18, "E": 18, "F": 18, "G": 2})

    title_block(ws, 2, "Data Overview & KPIs", span=5)

    # ---- Scale & Coverage (formula-driven) ----
    section_header(ws, 5, "Scale & Coverage")
    header_row(ws, 6, ["Metric", "Value"])
    overview_metrics = [
        ("Total orders", "#,##0"),
        ("Unique customers", "#,##0"),
        ("Sellers", "#,##0"),
        ("Products", "#,##0"),
        ("Product categories", "#,##0"),
        ("States covered", "0"),
        ("Cities covered", "#,##0"),
        ("Total GMV (R$)", "#,##0"),
        ("AOV (R$)", "0.00"),
    ]
    for i, (k, fmt) in enumerate(overview_metrics):
        r = 7 + i
        ws.cell(row=r, column=2, value=k).font = font(bold=True)
        ws.cell(row=r, column=2).fill = fill(LIGHT_GRAY)
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=2).alignment = left()
        c = ws.cell(row=r, column=3, value=kpi_lookup_formula(refs, k))
        c.number_format = fmt
        c.alignment = right()
        c.border = BORDER

    overview_end = 6 + len(overview_metrics)

    # ---- Yearly KPIs (formula-driven from tbl_yearly) ----
    yk_row = overview_end + 3
    section_header(ws, yk_row, "Year-over-Year KPIs")
    header_row(ws, yk_row + 1, ["Year", "GMV (R$ M)", "Orders", "Avg Review", "Avg Delivery (days)"])
    yearly = read_csv("kpi_yearly.csv")
    for i in range(len(yearly)):
        r = yk_row + 2 + i
        src_row = refs["yearly_start"] + i  # noqa: F841
        for ci, src_col in enumerate("ABCDE"):
            cell = ws.cell(row=r, column=2 + ci,
                           value=f"=_data_calc!{src_col}{refs['yearly_start'] + i}")
            cell.border = BORDER
            cell.alignment = center() if ci > 0 else left()
        ws.cell(row=r, column=3).number_format = "0.00"
        ws.cell(row=r, column=4).number_format = "#,##0"
        ws.cell(row=r, column=5).number_format = "0.00"
        ws.cell(row=r, column=6).number_format = "0.00"

    # ---- Order status (literals — small lookup table) ----
    st_row = yk_row + 2 + len(yearly) + 2
    section_header(ws, st_row, "Order Status Distribution")
    header_row(ws, st_row + 1, ["Status", "Orders", "Share %"])
    status = [
        ("delivered", 96478, 0.970),
        ("shipped", 1107, 0.011),
        ("canceled", 625, 0.006),
        ("unavailable", 609, 0.006),
        ("other", 622, 0.006),
    ]
    for i, (s, o, p) in enumerate(status):
        r = st_row + 2 + i
        ws.cell(row=r, column=2, value=s).border = BORDER
        c = ws.cell(row=r, column=3, value=o)
        c.number_format = "#,##0"; c.border = BORDER
        c2 = ws.cell(row=r, column=4, value=p)
        c2.number_format = "0.0%"; c2.border = BORDER
    st_end = st_row + 1 + len(status)
    add_table(ws, f"B{st_row + 1}:D{st_end}", "tbl_status")

    # ---- Payment mix ----
    pm_row = st_end + 3
    section_header(ws, pm_row, "Payment Mix (Brazil-specific)")
    header_row(ws, pm_row + 1, ["Payment type", "Orders", "Share %", "Avg installments"])
    payments = [
        ("credit_card", 76795, 0.739, 3.5),
        ("boleto", 19784, 0.190, 1.0),
        ("voucher", 5775, 0.056, 1.0),
        ("debit_card", 1529, 0.015, 1.0),
    ]
    for i, (p, o, share, inst) in enumerate(payments):
        r = pm_row + 2 + i
        ws.cell(row=r, column=2, value=p).border = BORDER
        c = ws.cell(row=r, column=3, value=o)
        c.number_format = "#,##0"; c.border = BORDER
        c2 = ws.cell(row=r, column=4, value=share)
        c2.number_format = "0.0%"; c2.border = BORDER
        c3 = ws.cell(row=r, column=5, value=inst)
        c3.number_format = "0.0"; c3.border = BORDER
    pm_end = pm_row + 1 + len(payments)
    add_table(ws, f"B{pm_row + 1}:E{pm_end}", "tbl_payment")

    ws.freeze_panes = "B5"


# ============================================================================
# 06_Revenue_Trend — formulas + Excel Table + chart
# ============================================================================
def build_revenue(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("06_Revenue_Trend")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 14, "C": 18, "D": 2})

    title_block(ws, 2, "Monthly Revenue Trend (2017–2018)", span=2)

    rev = read_csv("revenue.csv")
    header_row(ws, 5, ["Month", "Revenue (R$)"])
    for i in range(len(rev)):
        r = 6 + i
        src = refs["rev_start"] + i
        c1 = ws.cell(row=r, column=2, value=f"=_data_calc!A{src}")
        c1.border = BORDER
        c2 = ws.cell(row=r, column=3, value=f"=_data_calc!B{src}")
        c2.number_format = "#,##0"
        c2.border = BORDER
    end_row = 5 + len(rev)
    add_table(ws, f"B5:C{end_row}", "tbl_revenue_view")

    # Line chart
    chart = LineChart()
    chart.title = "Monthly Revenue (R$) — peak Nov 2017 (Black Friday + Christmas)"
    chart.y_axis.title = "Revenue (R$)"
    chart.x_axis.title = "Month"
    chart.height = 10
    chart.width = 22
    data = Reference(ws, min_col=3, min_row=5, max_row=end_row, max_col=3)
    cats = Reference(ws, min_col=2, min_row=6, max_row=end_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.style = 12
    ws.add_chart(chart, "E5")

    ws.freeze_panes = "B6"


# ============================================================================
# 07_RFM_Segments — formulas, no emoji, icon set conditional formatting
# ============================================================================
def build_rfm(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("07_RFM_Segments")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 22, "C": 14, "D": 14, "E": 14, "F": 14, "G": 18, "H": 14, "I": 32, "J": 2})

    title_block(ws, 2, "RFM Customer Segmentation",
                "Champions + At-Risk = 40% customers, 67% revenue.",
                span=8)

    persona_map = {
        "Champions": "Big-ticket buyer, ordered last month — protect, upsell",
        "At Risk": "High-value customer dormant ~13 months — top win-back priority",
        "Average": "Mid-frequency, mid-value. Cross-sell test bed",
        "Loyal Low-spend": "Recent + frequent but low ticket. Bundle / category expansion",
        "Lost": "Long inactive + low value. Lowest priority",
        "Potential New": "Just acquired, low ticket. Onboarding nurture",
    }

    header_row(ws, 5, ["Segment", "Customers", "Customer %", "Revenue (R$)",
                       "Revenue %", "ARPU (R$)", "Avg Recency (d)", "Persona / Action"])

    # Read data to get count + segment names in priority order
    rfm = read_csv("rfm_segments.csv")
    seg_map = {
        "冠軍客戶": "Champions", "流失風險": "At Risk", "一般客戶": "Average",
        "忠誠客戶": "Loyal Low-spend", "已流失": "Lost", "潛力新客": "Potential New",
    }
    priority = ["冠軍客戶", "流失風險", "忠誠客戶", "一般客戶", "潛力新客", "已流失"]
    rfm_sorted = sorted(rfm, key=lambda r: priority.index(r["segment"]))

    for i, row in enumerate(rfm_sorted):
        r = 6 + i
        en = seg_map[row["segment"]]
        src = refs["rfm_start"] + i
        # Segment name (literal — known business label)
        ws.cell(row=r, column=2, value=en).font = font(bold=True)
        # Numeric columns pull from _data_calc
        for ci, src_col in enumerate("BCDEFG"):
            cell = ws.cell(row=r, column=3 + ci,
                           value=f"=_data_calc!{src_col}{src}")
            cell.border = BORDER
        ws.cell(row=r, column=3).number_format = "#,##0"   # Customers
        ws.cell(row=r, column=4).number_format = "0.0%"    # Customer %
        ws.cell(row=r, column=5).number_format = "#,##0"   # Revenue
        ws.cell(row=r, column=6).number_format = "0.0%"    # Revenue %
        ws.cell(row=r, column=7).number_format = "0"       # ARPU
        ws.cell(row=r, column=8).number_format = "0"       # Recency
        # Persona
        p = ws.cell(row=r, column=9, value=persona_map[en])
        p.alignment = left()
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=9).border = BORDER

    end_row = 5 + len(rfm_sorted)
    add_table(ws, f"B5:I{end_row}", "tbl_rfm_view")

    # Conditional formatting:
    # - Data bar on Customer %
    # - Data bar on Revenue %
    # - 3-symbol icon set on ARPU (high/mid/low ARPU)
    ws.conditional_formatting.add(
        f"D6:D{end_row}",
        DataBarRule(start_type="min", end_type="max", color=TEAL,
                    showValue=True),
    )
    ws.conditional_formatting.add(
        f"F6:F{end_row}",
        DataBarRule(start_type="min", end_type="max", color=ORANGE,
                    showValue=True),
    )
    ws.conditional_formatting.add(
        f"G6:G{end_row}",
        IconSetRule("3TrafficLights1", "percent", [0, 33, 67], showValue=True),
    )

    # Bar chart: customer % vs revenue %
    chart = BarChart()
    chart.type = "bar"
    chart.style = 12
    chart.title = "Customer share vs Revenue share — Pareto: Champions+At-Risk = 39.7% / 66.9%"
    chart.y_axis.title = "Segment"
    chart.x_axis.title = "Share"
    chart.height = 10
    chart.width = 22
    data1 = Reference(ws, min_col=4, min_row=5, max_row=end_row, max_col=4)
    data2 = Reference(ws, min_col=6, min_row=5, max_row=end_row, max_col=6)
    cats = Reference(ws, min_col=2, min_row=6, max_row=end_row)
    chart.add_data(data1, titles_from_data=True)
    chart.add_data(data2, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, f"B{end_row + 3}")

    ws.freeze_panes = "B6"


# ============================================================================
# 08_Cohort_Heatmap — frozen panes + color scale
# ============================================================================
def build_cohort(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("08_Cohort_Heatmap")
    ws.sheet_view.showGridLines = False

    title_block(ws, 2, "Cohort Retention Heatmap",
                "Cell = % of cohort active in month N (benchmark M1: 5-15%).",
                span=14)

    months = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
    header_row(ws, 5, ["Cohort"] + months)
    set_col_widths(ws, {"A": 2, "B": 12} | {get_column_letter(i): 8 for i in range(3, 16)})

    cohort = read_csv("cohort_retention.csv")
    for i in range(len(cohort)):
        r = 6 + i
        src = refs["cohort_start"] + i
        ws.cell(row=r, column=2, value=f"=_data_calc!A{src}").font = font(bold=True)
        ws.cell(row=r, column=2).fill = fill(LIGHT_GRAY)
        ws.cell(row=r, column=2).border = BORDER
        for j in range(len(months)):
            src_col = get_column_letter(2 + j)  # B..N in _data_calc
            cell = ws.cell(row=r, column=3 + j,
                           value=f"=_data_calc!{src_col}{src}")
            cell.number_format = "0.0%"
            cell.alignment = center()
            cell.border = BORDER
            cell.font = font(size=9)

    end_row = 5 + len(cohort)
    add_table(ws, f"B5:O{end_row}", "tbl_cohort_view")

    # Color scale on M1+ (skip M0 which is always 100%)
    rule = ColorScaleRule(
        start_type="num", start_value=0, start_color="FFFFFF",
        mid_type="num", mid_value=0.05, mid_color=ACCENT_YELLOW,
        end_type="num", end_value=0.10, end_color=ORANGE,
    )
    ws.conditional_formatting.add(f"D6:O{end_row}", rule)

    ws.freeze_panes = "C6"


# ============================================================================
# 09_ROI_Calculator — Named Ranges + live formulas
# ============================================================================
def build_roi(wb: Workbook) -> None:
    ws = wb.create_sheet("09_ROI_Calculator")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 32, "C": 18, "D": 18, "E": 18, "F": 18, "G": 18, "H": 2})

    title_block(ws, 2, "At-Risk Win-back ROI Calculator",
                "Edit yellow cells — scenarios recompute live.",
                span=6)

    # ---- Inputs ----
    section_header(ws, 5, "INPUTS — edit me")
    header_row(ws, 6, ["Parameter", "Value", "Format", "Notes"])
    inputs = [
        ("At-risk customers (segment size)", 21975, "#,##0",
         "From RFM analysis", "At_Risk_Count"),
        ("Avg ARPU per customer (R$)", 213, "0",
         "Historical average for At-Risk segment", "ARPU"),
        ("Repeat-spend rate (% of ARPU on win-back order)", 0.50, "0%",
         "Conservative: assumes win-back order = 50% of historical average", "Repeat_Spend"),
        ("Total CRM cost (R$)", 50000, "#,##0",
         "Email + discount voucher budget", "CRM_Cost"),
    ]
    for i, (label, val, fmt, note, _name) in enumerate(inputs):
        r = 7 + i
        ws.cell(row=r, column=2, value=label).font = font(bold=True)
        c = ws.cell(row=r, column=3, value=val)
        c.fill = fill(ACCENT_YELLOW)
        c.font = font(bold=True, size=12)
        c.alignment = center()
        c.number_format = fmt
        medium_orange = Side(style="medium", color=ORANGE)
        c.border = Border(left=medium_orange, right=medium_orange,
                          top=medium_orange, bottom=medium_orange)
        ws.cell(row=r, column=4, value=fmt).font = font(italic=True, size=9, color=DARK_GRAY)
        ws.cell(row=r, column=5, value=note).font = font(italic=True, size=9, color=DARK_GRAY)
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=4).border = BORDER
        ws.cell(row=r, column=5).border = BORDER

    # Named Ranges for inputs (point at the value cells C7..C10)
    add_named_range(wb, "At_Risk_Count", "09_ROI_Calculator", "$C$7")
    add_named_range(wb, "ARPU", "09_ROI_Calculator", "$C$8")
    add_named_range(wb, "Repeat_Spend", "09_ROI_Calculator", "$C$9")
    add_named_range(wb, "CRM_Cost", "09_ROI_Calculator", "$C$10")

    # ---- Scenarios ----
    section_header(ws, 13, "SCENARIO OUTPUTS — recomputes live")
    header_row(ws, 14, ["Metric", "Conservative (5%)", "Optimistic (10%)",
                        "Aggressive (20%)", "Custom"])

    scenarios = [("D", 0.05), ("E", 0.10), ("F", 0.20), ("G", 0.10)]
    # Recall rate row
    ws.cell(row=15, column=2, value="Recall rate (%)").font = font(bold=True)
    ws.cell(row=15, column=2).border = BORDER
    for col_letter, default in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        c = ws.cell(row=15, column=col_idx, value=default)
        c.fill = fill(ACCENT_YELLOW if col_letter == "G" else LIGHT_GRAY)
        c.number_format = "0%"
        c.alignment = center()
        c.font = font(bold=True)
        c.border = BORDER

    # Recalled customers — uses Named Range At_Risk_Count
    ws.cell(row=16, column=2, value="Recalled customers").font = font(bold=True)
    ws.cell(row=16, column=2).border = BORDER
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=16, column=col_idx, value=f"=At_Risk_Count*{col_letter}15")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # Incremental revenue — uses Named Ranges
    ws.cell(row=17, column=2, value="Incremental revenue (R$)").font = font(bold=True)
    ws.cell(row=17, column=2).border = BORDER
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=17, column=col_idx,
                       value=f"=At_Risk_Count*{col_letter}15*ARPU*Repeat_Spend")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # CRM cost
    ws.cell(row=18, column=2, value="CRM cost (R$)").font = font(bold=True)
    ws.cell(row=18, column=2).border = BORDER
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=18, column=col_idx, value="=CRM_Cost")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER

    # Net = revenue - cost
    ws.cell(row=19, column=2, value="Net contribution (R$)").font = font(bold=True)
    ws.cell(row=19, column=2).border = BORDER
    for col_letter, _ in scenarios:
        col_idx = ord(col_letter) - ord("A") + 1
        cell = ws.cell(row=19, column=col_idx, value=f"={col_letter}17-{col_letter}18")
        cell.number_format = "#,##0"
        cell.alignment = center()
        cell.border = BORDER
        cell.font = font(bold=True)

    # ROI
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

    # Formula explanation
    section_header(ws, 22, "FORMULA")
    ws.cell(row=23, column=2,
            value="Incremental revenue  =  At_Risk_Count × Recall rate × ARPU × Repeat_Spend").font = font(italic=True)
    ws.cell(row=24, column=2,
            value="ROI                  =  Incremental revenue ÷ CRM_Cost").font = font(italic=True)



# ============================================================================
# 10_Installments — formulas, icon set
# ============================================================================
def build_installments(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("10_Installments")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 22, "C": 14, "D": 18, "E": 14, "F": 18, "G": 2})

    title_block(ws, 2, "Installments — AOV & Repeat Rate by Bucket",
                "73.9% of orders use credit_card, avg 3.5 installments.",
                span=5)

    inst = read_csv("installments.csv")
    header_row(ws, 5, ["Installment bucket", "Orders", "Avg ticket (R$)", "Customers", "Repeat rate"])
    for i in range(len(inst)):
        r = 6 + i
        src = refs["inst_start"] + i
        for ci, src_col in enumerate("ABCDE"):
            cell = ws.cell(row=r, column=2 + ci, value=f"=_data_calc!{src_col}{src}")
            cell.border = BORDER
        ws.cell(row=r, column=3).number_format = "#,##0"
        ws.cell(row=r, column=4).number_format = "0"
        ws.cell(row=r, column=5).number_format = "#,##0"
        ws.cell(row=r, column=6).number_format = "0.00%"

    end_row = 5 + len(inst)
    add_table(ws, f"B5:F{end_row}", "tbl_inst_view")

    # Conditional formatting: data bar on Avg ticket, icon set on Repeat rate
    ws.conditional_formatting.add(
        f"D6:D{end_row}",
        DataBarRule(start_type="min", end_type="max", color=TEAL, showValue=True),
    )
    ws.conditional_formatting.add(
        f"F6:F{end_row}",
        IconSetRule("3TrafficLights1", "percent", [0, 33, 67], showValue=True),
    )

    # AOV bar chart
    bar = BarChart()
    bar.type = "col"
    bar.style = 12
    bar.title = "Avg ticket (R$) by installment bucket — 7-10 installments = 3.48× single-payment"
    bar.y_axis.title = "Avg ticket (R$)"
    bar.x_axis.title = "Installments"
    bar.height = 9
    bar.width = 18
    data = Reference(ws, min_col=4, min_row=5, max_row=end_row, max_col=4)
    cats = Reference(ws, min_col=2, min_row=6, max_row=end_row)
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    ws.add_chart(bar, f"B{end_row + 3}")

    # Repeat rate bar chart
    bar2 = BarChart()
    bar2.type = "col"
    bar2.style = 13
    bar2.title = "Repeat rate by installment bucket — 7+ installment customers retain 65% better"
    bar2.y_axis.title = "Repeat rate"
    bar2.x_axis.title = "Installments"
    bar2.height = 9
    bar2.width = 18
    data2 = Reference(ws, min_col=6, min_row=5, max_row=end_row, max_col=6)
    bar2.add_data(data2, titles_from_data=True)
    bar2.set_categories(cats)
    ws.add_chart(bar2, f"B{end_row + 22}")

    ws.freeze_panes = "B6"


# ============================================================================
# 11_Logistics — formulas + 3-color scale
# ============================================================================
def build_logistics(wb: Workbook, refs: dict) -> None:
    ws = wb.create_sheet("11_Logistics")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 12, "C": 18, "D": 18, "E": 18, "F": 2})

    title_block(ws, 2, "Logistics — Estimated vs Actual Delivery (by State)",
                "National avg: 15.4 actual / 24 ETA days (36% under-promise).",
                span=4)

    log = read_csv("logistics.csv")
    header_row(ws, 5, ["State", "Actual days", "Estimated days", "ETA gap (days)"])
    for i in range(len(log)):
        r = 6 + i
        src = refs["log_start"] + i
        for ci, src_col in enumerate("ABCD"):
            cell = ws.cell(row=r, column=2 + ci, value=f"=_data_calc!{src_col}{src}")
            cell.border = BORDER
        ws.cell(row=r, column=2).font = font(bold=True)
        ws.cell(row=r, column=3).number_format = "0.0"
        ws.cell(row=r, column=4).number_format = "0.0"
        ws.cell(row=r, column=5).number_format = "0.0"

    end_row = 5 + len(log)
    add_table(ws, f"B5:E{end_row}", "tbl_logistics_view")

    # 3-color scale on ETA gap
    rule = ColorScaleRule(
        start_type="min", start_color="63BE7B",  # green = small gap (well-calibrated)
        mid_type="percentile", mid_value=50, mid_color="FFEB84",  # yellow
        end_type="max", end_color="F8696B",  # red = huge gap (over-promised buffer)
    )
    ws.conditional_formatting.add(f"E6:E{end_row}", rule)

    # Data bars on actual + estimated
    ws.conditional_formatting.add(
        f"C6:C{end_row}",
        DataBarRule(start_type="min", end_type="max", color=TEAL, showValue=True),
    )
    ws.conditional_formatting.add(
        f"D6:D{end_row}",
        DataBarRule(start_type="min", end_type="max", color=ORANGE, showValue=True),
    )

    # Bar chart
    chart = BarChart()
    chart.type = "bar"
    chart.style = 12
    chart.title = "Actual vs Estimated delivery days — SP best (8.8d), RN worst (19.3d)"
    chart.height = 14
    chart.width = 22
    data = Reference(ws, min_col=3, min_row=5, max_row=end_row, max_col=4)
    cats = Reference(ws, min_col=2, min_row=6, max_row=end_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "G5")

    ws.freeze_panes = "B6"


# ============================================================================
# 12_Methodology
# ============================================================================
def build_methodology(wb: Workbook) -> None:
    ws = wb.create_sheet("12_Methodology")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {"A": 2, "B": 24, "C": 60, "D": 30, "E": 2})

    title_block(ws, 2, "Methodology & Tech Stack", span=3)

    section_header(ws, 4, "Tech stack & why")
    stack = [
        ("Python 3.12", "Glue language for ETL + analysis"),
        ("SQLite + SQL", "9-table schema; SQL Window Functions for RFM (NTILE)"),
        ("pandas", "Cohort matrix + installment bucketing"),
        ("matplotlib", "Static portfolio charts (cohort, installments)"),
        ("Streamlit", "Interactive 5-page dashboard with ROI calculator"),
        ("Tableau Public", "Stakeholder-facing dashboard"),
        ("openpyxl", "This Excel portfolio (Tables, formulas, conditional formatting)"),
    ]
    header_row(ws, 5, ["Tool", "Role"])
    for i, (k, v) in enumerate(stack):
        r = 6 + i
        ws.cell(row=r, column=2, value=k).font = font(bold=True)
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=3, value=v).alignment = left()
        ws.cell(row=r, column=3).border = BORDER
    add_table(ws, f"B5:C{5 + len(stack)}", "tbl_stack")

    section_header(ws, 14, "Core SQL — RFM with NTILE Window Function")
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
    ws.row_dimensions[15].height = 380

    section_header(ws, 17, "Why NTILE (SQL) over pandas qcut")
    table = [
        ("Portability", "Snowflake / BigQuery / Redshift / SQLite all run identical SQL", "Python only"),
        ("Scale", "Runs in DB — handles tens of millions of rows", "Pulls all rows into Python memory"),
        ("Orchestration", "Slots into dbt / Airflow", "Needs custom wrapper"),
        ("Hiring signal", "'Knows the warehouse' = senior signal", "'Knows pandas' = junior signal"),
    ]
    header_row(ws, 18, ["Dimension", "NTILE (SQL)", "pandas qcut"])
    for i, (dim, a, b) in enumerate(table):
        r = 19 + i
        ws.cell(row=r, column=2, value=dim).font = font(bold=True)
        ws.cell(row=r, column=2).border = BORDER
        ws.cell(row=r, column=3, value=a).alignment = left()
        ws.cell(row=r, column=3).border = BORDER
        ws.cell(row=r, column=4, value=b).alignment = left()
        ws.cell(row=r, column=4).border = BORDER
    add_table(ws, f"B18:D{18 + len(table)}", "tbl_compare_ntile")

    section_header(ws, 24, "Caveats")
    caveats = [
        "F dimension near-zero variance — segmentation effectively R × M.",
        "2018 data truncated at 2018-10 (post-Sep dip = cutoff, not decline).",
        "Installments → AOV causality not established (needs A/B test).",
    ]
    for i, t in enumerate(caveats):
        c = ws.cell(row=25 + i, column=2, value=f"• {t}")
        c.font = font(); c.alignment = left()

    section_header(ws, 30, "Upgrade path (manual)")
    upgrade = [
        "Power Query: Data → Get Data → From Folder → /data. Each CSV becomes a Query.",
        "Power Pivot: load Queries to Data Model. Build orders→customers, items→orders, payments→orders.",
        "DAX measure: `Total Revenue := SUMX(items, items[price] + items[freight_value])`.",
        "Dashboard: replace literals with `=CUBEVALUE(\"ThisWorkbookDataModel\", \"[Measures].[…]\")`.",
    ]
    for i, t in enumerate(upgrade):
        c = ws.cell(row=31 + i, column=2, value=f"• {t}")
        c.font = font(); c.alignment = left()


# ============================================================================
# 13_Pivot_Analysis — VLOOKUP demo + SUMIFS PivotTable equivalent
# ============================================================================
def build_pivot_analysis(wb: Workbook) -> None:
    ws = wb.create_sheet("13_Pivot_Analysis")
    ws.sheet_view.showGridLines = False
    set_col_widths(ws, {
        "A": 2, "B": 26, "C": 22, "D": 22, "E": 22, "F": 14, "G": 14, "H": 14,
        "I": 4, "J": 14, "K": 14, "L": 12, "M": 4, "N": 26, "O": 26, "P": 2,
    })

    title_block(ws, 2, "Lookup & Pivot Demo", span=14)

    # =============================================================
    # SECTION A — Lookup demo: 5 rows, 3 methods side-by-side
    # =============================================================
    section_header(ws, 5, "A. Lookup — PT category → EN (3 methods, same result)")

    # Source table (right side) — keep all 71 rows so the lookup has real data
    translation = read_category_translation()
    ws.cell(row=5, column=14, value="Source: tbl_category_translation").font = font(bold=True, color=NAVY)
    header_row(ws, 6, ["PT name", "EN name"], start_col=14)
    for i, (pt, en) in enumerate(translation):
        r = 7 + i
        ws.cell(row=r, column=14, value=pt).font = Font(name="Consolas", size=10)
        ws.cell(row=r, column=15, value=en).font = Font(name="Consolas", size=10)
        ws.cell(row=r, column=14).border = BORDER
        ws.cell(row=r, column=15).border = BORDER
    trans_end = 6 + len(translation)
    add_table(ws, f"N6:O{trans_end}", "tbl_category_translation")

    # Demo: 5 PT categories × 3 lookup methods
    sample_pt = [pt for pt, _ in translation[:5]]
    header_row(ws, 7, ["PT input", "VLOOKUP result", "INDEX/MATCH result", "XLOOKUP result"])
    for i, pt in enumerate(sample_pt):
        r = 8 + i
        c1 = ws.cell(row=r, column=2, value=pt)
        c1.font = Font(name="Consolas", size=10); c1.border = BORDER
        # VLOOKUP — classic, leftmost-only
        c2 = ws.cell(row=r, column=3,
                     value=f'=VLOOKUP(B{r},$N$7:$O${trans_end},2,FALSE)')
        c2.font = Font(name="Consolas", size=10); c2.border = BORDER
        # INDEX/MATCH — universal, works on every Excel version since 1997
        c3 = ws.cell(row=r, column=4,
                     value=f'=INDEX($O$7:$O${trans_end},MATCH(B{r},$N$7:$N${trans_end},0))')
        c3.font = Font(name="Consolas", size=10); c3.border = BORDER
        # XLOOKUP — modern (Excel 2021+/365). _xlfn. prefix needed when
        # written by openpyxl so Excel recognizes the function.
        c4 = ws.cell(row=r, column=5,
                     value=f'=_xlfn.XLOOKUP(B{r},$N$7:$N${trans_end},$O$7:$O${trans_end},"not found")')
        c4.font = Font(name="Consolas", size=10); c4.border = BORDER

    # Compact comparison table directly under the demo
    section_header(ws, 14, "When to use which")
    header_row(ws, 15, ["Function", "Excel version", "When to use", "Trade-off"])
    methods = [
        ("VLOOKUP", "Any (since 2007)",
         "Quick lookup when key is in the leftmost column of the source table",
         "Breaks if columns get reordered (col_index is positional)"),
        ("INDEX/MATCH", "Any (since 1997)",
         "Universal fallback; key column can be anywhere in the source",
         "Slightly more verbose"),
        ("XLOOKUP", "Excel 2021 / 365 only",
         "Modern default — readable, supports if_not_found, bidirectional",
         "Falls back to #NAME? on older Excel"),
    ]
    for i, (fn, ver, when, trade) in enumerate(methods):
        r = 16 + i
        ws.cell(row=r, column=2, value=fn).font = Font(name="Consolas", size=10, bold=True)
        ws.cell(row=r, column=3, value=ver).font = font(size=10)
        ws.cell(row=r, column=4, value=when).font = font(size=10)
        ws.cell(row=r, column=4).alignment = left()
        ws.cell(row=r, column=5, value=trade).font = font(size=10)
        ws.cell(row=r, column=5).alignment = left()
        for col in (2, 3, 4, 5):
            ws.cell(row=r, column=col).border = BORDER
    add_table(ws, f"B15:E{15 + len(methods)}", "tbl_lookup_methods")

    # =============================================================
    # SECTION B — PivotTable equivalent: State × Payment Type
    # =============================================================
    section_header(ws, 24, "B. SUMIFS pivot — orders by State × Payment Type")

    # Compute aggregation
    states, ptypes, pivot_data = aggregate_state_payment()

    # ---- Long-form source table (right side, columns J:L) ----
    ws.cell(row=24, column=10, value="Long-form source").font = font(bold=True, color=NAVY)
    header_row(ws, 27, ["State", "Payment type", "Orders"], start_col=10)
    long_rows: list[tuple[str, str, int]] = []
    for s in states:
        for p in ptypes:
            v = pivot_data.get((s, p), 0)
            if v > 0:
                long_rows.append((s, p, v))
    for i, (s, p, v) in enumerate(long_rows):
        r = 28 + i
        ws.cell(row=r, column=10, value=s).border = BORDER
        ws.cell(row=r, column=11, value=p).border = BORDER
        c = ws.cell(row=r, column=12, value=v); c.number_format = "#,##0"; c.border = BORDER
    long_end = 27 + len(long_rows)
    add_table(ws, f"J27:L{long_end}", "tbl_payments_long")

    # ---- Pivot output (left side) ----
    pivot_header_row = 27
    pivot_first_data_row = 28
    pivot_cols = ["State"] + ptypes + ["Total"]
    header_row(ws, pivot_header_row, pivot_cols)

    # Source ranges for SUMIFS (use absolute refs into the long-form table)
    state_col_ref = f"$J$28:$J${long_end}"
    ptype_col_ref = f"$K$28:$K${long_end}"
    orders_col_ref = f"$L$28:$L${long_end}"

    for i, s in enumerate(states):
        r = pivot_first_data_row + i
        ws.cell(row=r, column=2, value=s).font = font(bold=True)
        ws.cell(row=r, column=2).border = BORDER
        for ci, p in enumerate(ptypes):
            col_idx = 3 + ci  # C, D, E, F
            # SUMIFS: sum orders where state matches and payment_type matches
            cell = ws.cell(row=r, column=col_idx,
                           value=f'=SUMIFS({orders_col_ref},{state_col_ref},$B{r},{ptype_col_ref},{get_column_letter(col_idx)}${pivot_header_row})')
            cell.number_format = "#,##0"
            cell.alignment = right()
            cell.border = BORDER
        # Row total
        total_col_idx = 3 + len(ptypes)
        first_payment_letter = "C"
        last_payment_letter = get_column_letter(2 + len(ptypes))
        total_cell = ws.cell(row=r, column=total_col_idx,
                             value=f"=SUM({first_payment_letter}{r}:{last_payment_letter}{r})")
        total_cell.number_format = "#,##0"
        total_cell.font = font(bold=True)
        total_cell.alignment = right()
        total_cell.border = BORDER
        total_cell.fill = fill(LIGHT_GRAY)

    # Column total row
    pivot_data_end = pivot_first_data_row + len(states) - 1
    total_row = pivot_data_end + 1
    ws.cell(row=total_row, column=2, value="Total").font = font(bold=True, color=WHITE)
    ws.cell(row=total_row, column=2).fill = fill(NAVY)
    ws.cell(row=total_row, column=2).border = BORDER
    for ci, _ in enumerate(ptypes):
        col_idx = 3 + ci
        cl = get_column_letter(col_idx)
        cell = ws.cell(row=total_row, column=col_idx,
                       value=f"=SUM({cl}{pivot_first_data_row}:{cl}{pivot_data_end})")
        cell.number_format = "#,##0"
        cell.font = font(bold=True, color=WHITE)
        cell.fill = fill(NAVY)
        cell.alignment = right()
        cell.border = BORDER
    grand_col = get_column_letter(3 + len(ptypes))
    gc = ws.cell(row=total_row, column=3 + len(ptypes),
                 value=f"=SUM(C{pivot_first_data_row}:{get_column_letter(2+len(ptypes))}{pivot_data_end})")
    gc.number_format = "#,##0"
    gc.font = font(bold=True, color=WHITE)
    gc.fill = fill(ORANGE)
    gc.alignment = right()
    gc.border = BORDER

    # Conditional formatting on the pivot body — color scale highlights hotspots
    body_range = f"C{pivot_first_data_row}:{get_column_letter(2+len(ptypes))}{pivot_data_end}"
    ws.conditional_formatting.add(
        body_range,
        ColorScaleRule(
            start_type="min", start_color="FFFFFF",
            mid_type="percentile", mid_value=50, mid_color=ACCENT_YELLOW,
            end_type="max", end_color=ORANGE,
        ),
    )

    ws.freeze_panes = "B6"


# ============================================================================
# Build
# ============================================================================
def main() -> None:
    wb = Workbook()
    default = wb.active
    wb.remove(default)

    # Hidden helper first so other builders can reference its row layout
    refs = build_data_calc(wb)

    # Visible sheets in display order
    build_cover(wb, refs)
    build_toc(wb)
    build_data_dictionary(wb)
    build_summary(wb)
    build_kpis(wb, refs)
    build_revenue(wb, refs)
    build_rfm(wb, refs)
    build_cohort(wb, refs)
    build_roi(wb)
    build_installments(wb, refs)
    build_logistics(wb, refs)
    build_methodology(wb)
    build_pivot_analysis(wb)

    # Reorder: put _data_calc at the end (visually last though hidden);
    # set 01_Cover as the active sheet on open
    sheet_order = [
        "01_Cover", "02_TOC", "03_Data_Dictionary", "04_Executive_Summary",
        "05_KPI_Dashboard", "06_Revenue_Trend", "07_RFM_Segments", "08_Cohort_Heatmap",
        "09_ROI_Calculator", "10_Installments", "11_Logistics", "12_Methodology",
        "13_Pivot_Analysis",
        "_data_calc",
    ]
    wb._sheets = [wb[name] for name in sheet_order]
    wb.active = 0
    wb.save(XLSX_PATH)
    print(f"Wrote {XLSX_PATH} ({XLSX_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

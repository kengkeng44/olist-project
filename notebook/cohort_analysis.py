"""
Cohort Retention Analysis — Olist
產出 output/cohort_retention.png:每個 cohort 月份在後續 N 個月的回購率熱力圖。
驗證 README 第七章「F=1.0 全平台單次客」結論。
"""

from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Arial Unicode MS", "DejaVu Sans"]
mpl.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "olist.db"
OUT = ROOT / "output" / "cohort_retention.png"

QUERY = """
SELECT
    c.customer_unique_id,
    DATE(o.order_purchase_timestamp, 'start of month') AS order_month
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
"""

with sqlite3.connect(DB) as conn:
    df = pd.read_sql(QUERY, conn, parse_dates=["order_month"])

cohort_month = df.groupby("customer_unique_id")["order_month"].min().rename("cohort_month")
df = df.join(cohort_month, on="customer_unique_id")

df["months_since"] = (
    (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
    + (df["order_month"].dt.month - df["cohort_month"].dt.month)
)

cohort_pivot = (
    df.groupby(["cohort_month", "months_since"])["customer_unique_id"]
    .nunique()
    .unstack("months_since")
)

cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0) * 100

retention = retention.loc[retention.index >= "2017-01-01"]
retention = retention.iloc[:, : min(13, retention.shape[1])]

fig, ax = plt.subplots(figsize=(12, 8))
masked = np.ma.masked_invalid(retention.values)
cmap = mpl.colormaps.get_cmap("YlOrRd").copy()
cmap.set_bad("#f5f5f5")
im = ax.imshow(masked, cmap=cmap, aspect="auto", vmin=0, vmax=5)

for i in range(retention.shape[0]):
    for j in range(retention.shape[1]):
        v = retention.values[i, j]
        if np.isnan(v):
            continue
        if j == 0:
            txt = "100%"
        elif v < 0.05:
            txt = "0"
        else:
            txt = f"{v:.1f}"
        color = "white" if v > 2.5 else "black"
        ax.text(j, i, txt, ha="center", va="center", fontsize=8, color=color)

ax.set_xticks(range(retention.shape[1]))
ax.set_xticklabels([f"M{i}" for i in retention.columns])
ax.set_yticks(range(retention.shape[0]))
ax.set_yticklabels([d.strftime("%Y-%m") for d in retention.index])
ax.set_xlabel("購買後第 N 個月", fontsize=11)
ax.set_ylabel("Cohort 月份(首購月)", fontsize=11)

cohort_size_aligned = cohort_size.loc[retention.index]
y_labels = [f"{d.strftime('%Y-%m')}  (n={int(n):,})"
            for d, n in zip(retention.index, cohort_size_aligned)]
ax.set_yticklabels(y_labels)

cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("回購率 (%)", fontsize=10)

ax.set_title(
    "Olist Cohort 留存熱力圖 — 巴西電商客戶幾乎不回購\n"
    "M0 全部 100%(首購月);M1+ 普遍 < 1%,證實 F=1.0 平台特性",
    fontsize=12, pad=15,
)

plt.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=120, bbox_inches="tight")
print(f"saved: {OUT}")

ever_repeat = (df.groupby("customer_unique_id")["order_month"].nunique() > 1).sum()
total_customers = df["customer_unique_id"].nunique()
print(f"\n=== 摘要 ===")
print(f"Total unique customers: {total_customers:,}")
print(f"Customers with >1 purchase month: {ever_repeat:,} ({ever_repeat/total_customers*100:.2f}%)")
print(f"\n=== M1 retention by cohort (first 6 months shown) ===")
m1 = retention.iloc[:6, 1] if retention.shape[1] > 1 else None
if m1 is not None:
    print(m1.round(2).to_string())

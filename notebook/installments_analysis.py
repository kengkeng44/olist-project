"""
Installments Insight — Olist
分期付款是 Olist 的差異化賣點(巴西電商通病:分期文化盛行)。
本腳本驗證兩個假設:
  H1: 高分期 → 高客單價 (ARPU)
  H2: 高分期 → 高回購率 (這是 PM action 的關鍵)

產出 output/installments_insight.png:雙軸條形圖。
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
OUT = ROOT / "output" / "installments_insight.png"

ARPU_QUERY = """
SELECT CASE
  WHEN payment_installments = 1 THEN '1 (一次付清)'
  WHEN payment_installments BETWEEN 2 AND 3 THEN '2-3 期'
  WHEN payment_installments BETWEEN 4 AND 6 THEN '4-6 期'
  WHEN payment_installments BETWEEN 7 AND 10 THEN '7-10 期'
  ELSE '11+ 期'
END AS bucket,
ROUND(MIN(payment_installments), 0) AS sort_key,
COUNT(*) AS orders,
ROUND(AVG(payment_value), 2) AS avg_ticket
FROM order_payments
WHERE payment_type = 'credit_card' AND payment_installments >= 1
GROUP BY bucket
ORDER BY sort_key;
"""

REPEAT_QUERY = """
WITH first_order AS (
  SELECT c.customer_unique_id,
         MIN(o.order_purchase_timestamp) AS first_ts
  FROM customers c JOIN orders o USING(customer_id)
  WHERE o.order_status = 'delivered' GROUP BY c.customer_unique_id
),
first_install AS (
  SELECT c.customer_unique_id,
         MAX(p.payment_installments) AS payment_installments
  FROM customers c
  JOIN orders o ON c.customer_id = o.customer_id
  JOIN order_payments p ON o.order_id = p.order_id
  JOIN first_order f ON c.customer_unique_id = f.customer_unique_id
       AND o.order_purchase_timestamp = f.first_ts
  WHERE p.payment_type = 'credit_card'
  GROUP BY c.customer_unique_id
),
cust_orders AS (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
  FROM customers c JOIN orders o USING(customer_id)
  WHERE o.order_status = 'delivered' GROUP BY c.customer_unique_id
)
SELECT CASE
  WHEN payment_installments = 1 THEN '1 (一次付清)'
  WHEN payment_installments BETWEEN 2 AND 3 THEN '2-3 期'
  WHEN payment_installments BETWEEN 4 AND 6 THEN '4-6 期'
  WHEN payment_installments BETWEEN 7 AND 10 THEN '7-10 期'
  ELSE '11+ 期'
END AS bucket,
ROUND(MIN(payment_installments), 0) AS sort_key,
COUNT(*) AS customers,
ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_rate_pct
FROM first_install JOIN cust_orders USING(customer_unique_id)
GROUP BY bucket
ORDER BY sort_key;
"""

with sqlite3.connect(DB) as conn:
    arpu = pd.read_sql(ARPU_QUERY, conn).set_index("bucket")
    repeat = pd.read_sql(REPEAT_QUERY, conn).set_index("bucket")

df = arpu.join(repeat[["customers", "repeat_rate_pct"]])
print(df.to_string())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]

bars1 = ax1.bar(df.index, df["avg_ticket"], color=colors, edgecolor="white")
for b, v, n in zip(bars1, df["avg_ticket"], df["orders"]):
    ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 8,
             f"R$ {v:,.0f}", ha="center", fontsize=11, fontweight="bold")
    ax1.text(b.get_x() + b.get_width() / 2, b.get_height() / 2,
             f"n={n:,}", ha="center", color="white", fontsize=9)
ax1.set_ylabel("平均客單價 (R$)", fontsize=11)
ax1.set_title("分期數 → 客單價:7-10 期是一次付清的 3.5 倍", fontsize=12, pad=10)
ax1.set_ylim(0, df["avg_ticket"].max() * 1.18)
ax1.grid(axis="y", alpha=0.3)

bars2 = ax2.bar(df.index, df["repeat_rate_pct"], color=colors, edgecolor="white")
for b, v, n in zip(bars2, df["repeat_rate_pct"], df["customers"]):
    ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.08,
             f"{v:.2f}%", ha="center", fontsize=11, fontweight="bold")
    ax2.text(b.get_x() + b.get_width() / 2, b.get_height() / 2,
             f"n={n:,}", ha="center", color="white", fontsize=9)
ax2.set_ylabel("回購率 (% 客戶下過 >1 單)", fontsize=11)
ax2.set_title("分期數 → 回購率:7+ 期客戶回購率高 67%", fontsize=12, pad=10)
ax2.set_ylim(0, df["repeat_rate_pct"].max() * 1.25)
ax2.grid(axis="y", alpha=0.3)

baseline = df.loc["1 (一次付清)", "repeat_rate_pct"]
ax2.axhline(baseline, linestyle="--", color="gray", linewidth=1, alpha=0.6)
ax2.text(0, baseline + 0.05, f"baseline {baseline:.2f}%",
         color="gray", fontsize=8, va="bottom")

fig.suptitle(
    "巴西分期付款洞察:Olist 信用卡訂單(76,795 筆)分期數 vs ARPU & 回購率",
    fontsize=13, fontweight="bold", y=1.02,
)
plt.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=120, bbox_inches="tight")
print(f"\nsaved: {OUT}")

print("\n=== 摘要 ===")
hi = df.loc["7-10 期"]
lo = df.loc["1 (一次付清)"]
print(f"ARPU 倍數 (7-10 vs 1): {hi['avg_ticket']/lo['avg_ticket']:.2f}x")
print(f"回購率倍數 (7-10 vs 1): {hi['repeat_rate_pct']/lo['repeat_rate_pct']:.2f}x")
print(f"7+ 期客戶總數: {df.loc[['7-10 期','11+ 期'],'customers'].sum():,}")

"""Create Dataset/budget.csv.
  python scripts/get_dataset.py             -> try the original GitHub dataset, else synthetic
  python scripts/get_dataset.py --synthetic -> always generate the synthetic demo dataset
Schema used by the app: date_time, category, amount
"""
import sys, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(__file__).resolve().parent.parent / "Dataset" / "budget.csv"
URL = "https://raw.githubusercontent.com/Ismat-Samadov/Budget_Prediction/main/1.0.0/budget.csv"

def synthetic():
    rng = np.random.default_rng(7)
    cats = {  # category: (avg txns/month, mean amount, seasonality amplitude)
        "Rent": (1, 900, 0), "Groceries": (14, 38, .08), "Utilities": (3, 45, .25),
        "Transport": (12, 14, .05), "Dining Out": (8, 27, .15), "Entertainment": (5, 22, .2),
        "Shopping": (4, 70, .45), "Health": (2, 60, .1), "Travel": (1, 260, .9), "Education": (1, 120, .3)}
    rows = []
    for m in pd.date_range("2022-01-01", "2025-12-01", freq="MS"):
        t = (m.year - 2022) * 12 + m.month
        infl = 1 + .004 * t
        for c, (n, mu, amp) in cats.items():
            season = 1 + amp * (np.cos((m.month - 12) / 12 * 2 * np.pi) if c != "Utilities" else -np.cos(m.month / 12 * 2 * np.pi))
            for _ in range(1 if c == "Rent" else max(1, rng.poisson(n))):
                day = 1 if c == "Rent" else int(rng.integers(1, m.days_in_month + 1))
                amt = max(2, rng.normal(mu * infl * season, mu * .18))
                rows.append((m.replace(day=day).strftime("%Y-%m-%d"), c, round(float(amt), 2)))
    return pd.DataFrame(rows, columns=["date_time", "category", "amount"]).sort_values("date_time")

if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    if "--synthetic" not in sys.argv:
        try:
            urllib.request.urlretrieve(URL, OUT); print("Downloaded original dataset ->", OUT); sys.exit()
        except Exception as e:
            print("Download failed (", e, ") - generating synthetic dataset instead.")
    df = synthetic(); df.to_csv(OUT, index=False); print(f"Synthetic dataset: {len(df)} rows -> {OUT}")

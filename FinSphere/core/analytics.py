"""Analytics engine (pure numpy/pandas): data cleaning, K-Means clustering, expense forecasting."""
from pathlib import Path
import numpy as np
import pandas as pd


# ---------- 1. Load & clean ----------
def load_dataset(path):
    raw = pd.read_csv(path)
    raw.columns = [c.strip().lower() for c in raw.columns]
    raw = raw.rename(columns={"date": "date_time", "datetime": "date_time"})
    df = raw.copy()
    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()
    df["category"] = df["category"].astype("string").str.strip()
    df = df.dropna(subset=["date_time", "category", "amount"]).query("amount > 0")
    info = {"raw_rows": len(raw), "clean_rows": len(df), "removed": len(raw) - len(df),
            "start": df.date_time.min().strftime("%b %Y"), "end": df.date_time.max().strftime("%b %Y"),
            "categories": int(df.category.nunique()), "total": round(float(df.amount.sum()), 2)}
    return df, info


def category_table(df):
    g = df.groupby("category")["amount"].agg(total="sum", avg="mean", count="count").reset_index()
    g["share"] = (g.total / g.total.sum() * 100).round(1)
    return g.sort_values("total", ascending=False)


# ---------- 2. K-Means (k-means++ init, implemented from scratch) ----------
def kmeans(X, k, seed=42, iters=200):
    rng = np.random.default_rng(seed)
    cent = [X[rng.integers(len(X))]]
    for _ in range(k - 1):
        d = np.min([((X - c) ** 2).sum(1) for c in cent], axis=0)
        cent.append(X[rng.choice(len(X), p=d / d.sum())] if d.sum() > 0 else X[rng.integers(len(X))])
    cent = np.array(cent)
    for _ in range(iters):
        lab = ((X[:, None] - cent[None]) ** 2).sum(2).argmin(1)
        new = np.array([X[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(k)])
        if np.allclose(new, cent):
            break
        cent = new
    return lab, cent


def cluster_categories(df, k=3):
    t = category_table(df)
    F = np.log1p(t[["total", "avg", "count"]].to_numpy(float))
    Z = (F - F.mean(0)) / np.where(F.std(0) == 0, 1, F.std(0))
    k = max(1, min(k, len(t)))
    lab, _ = kmeans(Z, k)
    order = t.assign(c=lab).groupby("c")["total"].mean().sort_values(ascending=False).index.tolist()
    names = ["High-impact", "Mid-range", "Low-impact"] + [f"Group {i}" for i in range(4, k + 1)]
    rank = {c: i for i, c in enumerate(order)}
    lo, hi = F.min(0), F.max(0)
    pos = np.where(hi > lo, (F - lo) / np.where(hi > lo, hi - lo, 1) * 2 - 1, 0)
    out = []
    for i, r in enumerate(t.itertuples()):
        out.append({"category": r.category, "total": round(r.total, 2), "avg": round(r.avg, 2), "count": int(r.count),
                    "share": r.share, "cluster": rank[lab[i]], "label": names[rank[lab[i]]],
                    "x": float(pos[i, 0]), "y": float(pos[i, 1]), "z": float(pos[i, 2])})
    return out


# ---------- 3. Expense forecasting (ridge regression on trend + seasonality + lags) ----------
def _row(t, month, l1, l2):
    return [t, np.sin(2 * np.pi * month / 12), np.cos(2 * np.pi * month / 12), l1, l2]


def _fit(X, y, alpha=1.0):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1
    Z = np.c_[np.ones(len(X)), (X - mu) / sd]
    P = alpha * np.eye(Z.shape[1]); P[0, 0] = 0
    return mu, sd, np.linalg.solve(Z.T @ Z + P, Z.T @ y)


def _predict(m, X):
    mu, sd, w = m
    return np.c_[np.ones(len(X)), (X - mu) / sd] @ w


def monthly_series(df):
    s = df.set_index("date_time")["amount"].resample("MS").sum()
    return s[s > 0]


def build_forecaster(df):
    s = monthly_series(df)
    y, months = s.to_numpy(float), s.index
    if len(y) < 12:
        raise ValueError("Need at least 12 months of data to train the forecaster.")
    X = np.array([_row(i, months[i].month, y[i - 1], y[i - 2]) for i in range(2, len(y))])
    T = y[2:]
    cut = int(len(T) * 0.8)                                   # chronological 80/20 split (no shuffling = no leakage)
    m = _fit(X[:cut], T[:cut])
    pred = _predict(m, X[cut:])
    actual = T[cut:]
    err = actual - pred
    ss_res, ss_tot = (err ** 2).sum(), ((actual - actual.mean()) ** 2).sum()
    naive = np.abs(actual - X[cut:, 3]).mean()                # baseline: "same as last month"
    metrics = {"mae": float(np.abs(err).mean()), "rmse": float(np.sqrt((err ** 2).mean())),
               "r2": float(1 - ss_res / ss_tot) if ss_tot else 0.0,
               "mape": float((np.abs(err) / actual).mean() * 100), "baseline_mae": float(naive),
               "train_months": int(cut), "test_months": int(len(T) - cut)}
    final = _fit(X, T)
    return {"model": final, "y": y, "months": months, "metrics": metrics, "cut": cut, "test_pred": pred}


def forecast_month(fc, year, month):
    months, y = fc["months"], list(fc["y"])
    last = months[-1]
    h = (year - last.year) * 12 + (month - last.month)
    if h < -len(y) + 1 or h > 36:
        raise ValueError(f"Pick a month between {months[0]:%b %Y} and {(last + pd.DateOffset(months=36)):%b %Y}.")
    labels = [f"{d:%b %y}" for d in months]
    test_line = [None] * (2 + fc["cut"]) + [round(float(v), 2) for v in fc["test_pred"]]
    result = {"labels": labels, "actual": [round(v, 2) for v in y], "test_pred": test_line,
              "metrics": fc["metrics"], "target": f"{pd.Timestamp(year, month, 1):%B %Y}"}
    if h <= 0:
        result.update(kind="recorded", value=round(y[h - 1], 2))
        return result
    path = []
    for i in range(1, h + 1):
        d = last + pd.DateOffset(months=i)
        v = max(0.0, float(_predict(fc["model"], np.array([_row(len(y), d.month, y[-1], y[-2])]))[0]))
        y.append(v); path.append((f"{d:%b %y}", round(v, 2)))
    band = fc["metrics"]["rmse"]
    result.update(kind="forecast", value=path[-1][1], low=max(0, round(path[-1][1] - band, 2)),
                  high=round(path[-1][1] + band, 2),
                  future_labels=[p[0] for p in path], future=[p[1] for p in path])
    return result


# ---------- 4. Investment suggestion ----------
def recommend(income, expense):
    income, expense = float(income), float(expense)
    surplus = income - expense
    if surplus <= 0:
        return {"surplus": round(surplus, 2), "rate": 0, "plan": [], "headline": "Projected deficit",
                "advice": "Expected spending exceeds income. Trim the High-impact categories before investing."}
    rate = surplus / income
    if rate < 0.10:
        split, head = [("Emergency fund", 70), ("Index-fund SIP", 30)], "Build your safety net first"
    elif rate < 0.25:
        split, head = [("Emergency fund", 35), ("Index funds", 40), ("Bonds / fixed deposits", 25)], "Balanced growth"
    else:
        split, head = [("Emergency fund", 20), ("Equity index funds", 45), ("Bonds / fixed deposits", 20),
                       ("Skills & goals", 15)], "Growth-focused"
    return {"surplus": round(surplus, 2), "rate": round(rate * 100, 1), "headline": head,
            "plan": [{"name": n, "pct": p, "amount": round(surplus * p / 100, 2)} for n, p in split],
            "advice": "Educational suggestion based on your projected surplus - not financial advice."}

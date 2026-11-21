# FinSphere — AI Personal Finance Manager in 3D

Upgraded version of the "AI-Based Personal Finance Manager" project: modern stack, a Three.js 3D interface,
and an honest ML pipeline.

| Module | What it does |
|---|---|
| Sign up / Login + **Email OTP** | Django auth (hashed passwords), 6-digit OTP valid 5 min, max 5 tries |
| Dataset | Cleans `Dataset/budget.csv` (drops missing/invalid rows) and profiles it |
| **3D Clusters** | K-Means (k-means++) groups categories into High / Mid / Low-impact; orbit them in 3D |
| Forecast | Ridge regression on trend + seasonality + lag features; chronological 80/20 split; MAE, RMSE, R², MAPE vs a naive baseline |
| Budget | Pick a month + income → predicted expenses, likely range, suggested allocation |
| Feedback | VADER sentiment (Positive / Neutral / Negative) |

## What changed vs. the original
- Python 3.7 / Django 2.1 / TensorFlow 1.14 / MySQL → **Django 5.x, Python 3.10+, SQLite** (no database install).
- Heavy TF/Keras stack removed → numpy + pandas only (installs in seconds).
- Fixed: the old `test.py` overwrote predictions with `actual - random(3.5, 8.5)`, which fakes the accuracy. Metrics here come from real held-out data.
- Shuffled train/test split on time series (data leakage) → chronological split.

## Run in VS Code
1. Install Python 3.10+; open this folder in VS Code (`File → Open Folder`).
2. Terminal → Windows: `run.bat` · Mac/Linux: `./run.sh`  (creates `.venv`, installs, migrates, starts server)
3. Open http://127.0.0.1:8000 → Sign up → Sign in. **The OTP is printed in the VS Code terminal.**
   For real e-mail set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` (Gmail app-password) before starting.

The 3D scenes load Three.js / Chart.js from a CDN, so you need internet in the browser.

## Dataset
`Dataset/budget.csv` (columns `date_time, category, amount`) ships as a **synthetic stand-in** (2022–2025).
To use the original Kaggle/GitHub data run `python scripts/get_dataset.py`, or drop the real file into `Dataset/`.
The app reloads it automatically.

## Structure
```
finsphere/   settings, urls          core/analytics.py  clustering + forecasting
core/        views, models, OTP      core/templates, core/static  (3D UI)
Dataset/     budget.csv              scripts/get_dataset.py
```
Investment suggestions are educational, not financial advice.

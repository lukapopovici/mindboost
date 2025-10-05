#!/usr/bin/env python3
"""
Flask microservice for burnout risk prediction.

Start:
  flask --app predict_service run --host=0.0.0.0 --port=8000

Env:
  MODEL_PATH=/path/to/model.pkl  (default: ./model.pkl)

Request (JSON):
{
  "user_id": "u1",
  "series": [
    {"date": "2025-01-05", "score": 82},
    {"date": "2025-01-12", "score": 78},
    {"date": "2025-01-20", "score": 74}
  ]
}

Response:
{
  "user_id": "u1",
  "prob_close_to_burnout": 0.78,
  "features": {...}
}
"""

from flask import Flask, request, jsonify
from typing import List, Optional, Dict, Any
import os
import numpy as np
import pandas as pd
import joblib

# ---------- Feature extraction (must match training pipeline) ----------

def _as_day_index(series_datetime: pd.Series) -> np.ndarray:
    return series_datetime.view("int64") / (24*3600*1e9)

def _slope(y: pd.Series, x: Optional[pd.Series] = None) -> float:
    if len(y) < 2 or y.std(skipna=True) == 0:
        return 0.0
    if x is None:
        x = pd.Series(np.arange(len(y)), index=y.index)
    msk = np.isfinite(y.values) & np.isfinite(x.values)
    if msk.sum() < 2:
        return 0.0
    try:
        return float(np.polyfit(x.values[msk], y.values[msk], 1)[0])
    except Exception:
        return 0.0

def _window_slope(df: pd.DataFrame, days: int) -> float:
    if df.empty:
        return 0.0
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    sub = df[df["date"] >= cutoff]
    if len(sub) < 2:
        return 0.0
    return _slope(sub["score"], _as_day_index(sub["date"]))

def _max_drawdown(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    peak = values.cummax()
    drawdown = values - peak
    return float(drawdown.min())

def _safe_std(x: pd.Series) -> float:
    return float(x.std()) if len(x) > 1 else 0.0

def _ema(x: pd.Series, span: int) -> pd.Series:
    return x.ewm(span=span, adjust=False).mean()

def features_from_timeseries(records: List[Dict[str, Any]]) -> Dict[str, float]:
    df = pd.DataFrame(records)
    if "date" not in df or "score" not in df:
        raise ValueError("Each record must include 'date' and 'score'.")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").dropna(subset=["score"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])

    df["delta_score"] = df["score"].diff()
    df["days_between"] = df["date"].diff().dt.days
    df["change_per_day"] = df["delta_score"] / df["days_between"].replace(0, np.nan)

    n = len(df)
    if n == 0:
        raise ValueError("No valid rows after parsing date/score.")

    span_days = (df["date"].iloc[-1] - df["date"].iloc[0]).days if n >= 2 else 0

    slope_all = _slope(df["score"], _as_day_index(df["date"]))
    slope_14 = _window_slope(df, 14)
    slope_28 = _window_slope(df, 28)
    slope_56 = _window_slope(df, 56)

    rolling3_std = _safe_std(df["score"].rolling(3, min_periods=2).mean().dropna())
    recent_mean_3 = df["score"].tail(3).mean() if n >= 1 else np.nan
    recent_std_3 = df["score"].tail(3).std() if n >= 2 else 0.0

    ema_7 = _ema(df["score"], 7)
    ema_14 = _ema(df["score"], 14)
    ema_28 = _ema(df["score"], 28)

    last = df["score"].iloc[-1] if n else np.nan
    max_dd = _max_drawdown(df["score"])

    cadence_mean = float(df["days_between"].dropna().mean()) if n > 1 else 0.0
    cadence_std = float(df["days_between"].dropna().std()) if n > 2 else 0.0
    cadence_cv = (cadence_std / cadence_mean) if cadence_mean else 0.0

    last_2 = df["score"].iloc[-2] if n >= 2 else np.nan
    last_3 = df["score"].iloc[-3] if n >= 3 else np.nan

    f: Dict[str, float] = {
        "count_points": float(n),
        "span_days": float(span_days),
        "mean_score": float(df["score"].mean()) if n else np.nan,
        "std_score": float(df["score"].std()) if n > 1 else 0.0,
        "min_score": float(df["score"].min()) if n else np.nan,
        "max_score": float(df["score"].max()) if n else np.nan,
        "last_score": float(last) if n else np.nan,
        "last_minus_ema7": float(last - ema_7.iloc[-1]) if n else 0.0,
        "last_minus_ema14": float(last - ema_14.iloc[-1]) if n else 0.0,
        "last_minus_ema28": float(last - ema_28.iloc[-1]) if n else 0.0,
        "slope_all": float(slope_all),
        "slope_14d": float(slope_14),
        "slope_28d": float(slope_28),
        "slope_56d": float(slope_56),
        "rolling3_std": float(rolling3_std),
        "recent_mean_3": float(recent_mean_3) if not np.isnan(recent_mean_3) else 0.0,
        "recent_std_3": float(recent_std_3),
        "mean_change_per_day": float(df["change_per_day"].mean(skipna=True)) if n > 1 else 0.0,
        "median_change_per_day": float(df["change_per_day"].median(skipna=True)) if n > 1 else 0.0,
        "max_drawdown": float(max_dd),
        "cadence_mean_days": float(cadence_mean),
        "cadence_cv": float(cadence_cv),
        "last2_diff": float(last - last_2) if n >= 2 else 0.0,
        "last3_diff": float(last - last_3) if n >= 3 else 0.0,
    }
    for k, v in list(f.items()):
        if isinstance(v, float) and (not np.isfinite(v)):
            f[k] = 0.0
    return f

# ---------- Flask app ----------

MODEL_PATH = os.getenv("MODEL_PATH", "./model.pkl")

app = Flask(__name__)

def _load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"MODEL_PATH not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH)
    })

@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
        user_id = payload.get("user_id")
        series = payload.get("series", [])
        feats = features_from_timeseries(series)
        model = _load_model()
        X = pd.DataFrame([feats])
        try:
            prob = float(model.predict_proba(X)[0, 1])
        except Exception as e:
            if hasattr(model, "feature_names_in_"):
                cols_needed = list(model.feature_names_in_)
                for c in cols_needed:
                    if c not in X.columns:
                        X[c] = 0.0
                X = X[cols_needed]
                prob = float(model.predict_proba(X)[0, 1])
            else:
                raise
        return jsonify({
            "user_id": user_id,
            "prob_close_to_burnout": prob,
            "features": feats
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unhandled error: {type(e).__name__}: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

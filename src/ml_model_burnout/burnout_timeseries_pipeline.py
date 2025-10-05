#!/usr/bin/env python3
"""
Burnout Time‑Series Pipeline (single-file)

Usage:
  python burnout_timeseries_pipeline.py \
    --scores scores.json \
    --labels labels.json \
    --outdir ./out \
    [--user-id SINGLE_USER_ID]

Input formats
-------------
scores.json : either of
A) List of dicts with user_id:
   [
     {"user_id": "u1", "date": "2025-01-05", "score": 82},
     {"user_id": "u1", "date": "2025-01-12", "score": 78},
     {"user_id": "u2", "date": "2025-01-06", "score": 91}
   ]

B) List of dicts without user_id (single user file): provide --user-id
   [
     {"date": "2025-01-05", "score": 82},
     {"date": "2025-01-12", "score": 78}
   ]

labels.json :
   [
     {"user_id": "u1", "close_to_burnout": true},
     {"user_id": "u2", "close_to_burnout": false}
   ]

Outputs
-------
- <outdir>/features.csv      : feature table per user_id
- <outdir>/model.pkl         : trained model (if labels provided)
- <outdir>/metrics.txt       : CV metrics (if labels provided)

Notes
-----
- Features summarize recent level, trend, volatility, cadence, drawdowns.
- We perform GroupKFold CV by user to avoid leakage across a user's time slices.
"""

import argparse, json, math, os, sys
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import joblib


def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in ["date", "score"] if c not in df.columns]
    if missing:
        raise ValueError(f"scores JSON missing required fields: {missing}")
    return df


def _as_day_index(series_datetime: pd.Series) -> np.ndarray:
    # Convert datetime to float number of days since epoch (for stable regression)
    return series_datetime.view("int64") / (24*3600*1e9)


def _slope(y: pd.Series, x: Optional[pd.Series] = None) -> float:
    if len(y) < 2 or y.std(skipna=True) == 0:
        return 0.0
    if x is None:
        x = pd.Series(np.arange(len(y)), index=y.index)
    # Use polyfit on finite values only
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
    # Max peak-to-trough drop (negative number or 0)
    if values.empty:
        return 0.0
    peak = values.cummax()
    drawdown = values - peak
    return float(drawdown.min())  # most negative drop


def _safe_std(x: pd.Series) -> float:
    return float(x.std()) if len(x) > 1 else 0.0


def _ema(x: pd.Series, span: int) -> pd.Series:
    return x.ewm(span=span, adjust=False).mean()


def features_from_timeseries(df_user: pd.DataFrame) -> Dict[str, float]:
    """Compute a robust set of features from one user's time series."""
    df = df_user.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").dropna(subset=["score"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])

    # Basic deltas & cadence
    df["delta_score"] = df["score"].diff()
    df["days_between"] = df["date"].diff().dt.days
    df["change_per_day"] = df["delta_score"] / df["days_between"].replace(0, np.nan)

    # Level, spread, count, span
    n = len(df)
    span_days = (df["date"].iloc[-1] - df["date"].iloc[0]).days if n >= 2 else 0

    # Trend slopes (overall and recent windows)
    slope_all = _slope(df["score"], _as_day_index(df["date"]))
    slope_14 = _window_slope(df, 14)
    slope_28 = _window_slope(df, 28)
    slope_56 = _window_slope(df, 56)

    # Volatility & recent momentum
    rolling3_std = _safe_std(df["score"].rolling(3, min_periods=2).mean().dropna())
    recent_mean_3 = df["score"].tail(3).mean() if n >= 1 else np.nan
    recent_std_3 = df["score"].tail(3).std() if n >= 2 else 0.0

    # EMAs
    ema_7 = _ema(df["score"], 7)
    ema_14 = _ema(df["score"], 14)
    ema_28 = _ema(df["score"], 28)

    last = df["score"].iloc[-1] if n else np.nan

    # Drawdown
    max_dd = _max_drawdown(df["score"])

    # Cadence irregularity
    cadence_mean = float(df["days_between"].dropna().mean()) if n > 1 else 0.0
    cadence_std = float(df["days_between"].dropna().std()) if n > 2 else 0.0
    cadence_cv = (cadence_std / cadence_mean) if cadence_mean else 0.0

    # Last-N momentum
    last_1 = last
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
        "recent_mean_3": float(recent_mean_3) if not math.isnan(recent_mean_3) else 0.0,
        "recent_std_3": float(recent_std_3),

        "mean_change_per_day": float(df["change_per_day"].mean(skipna=True)) if n > 1 else 0.0,
        "median_change_per_day": float(df["change_per_day"].median(skipna=True)) if n > 1 else 0.0,

        "max_drawdown": float(max_dd),
        "cadence_mean_days": float(cadence_mean),
        "cadence_cv": float(cadence_cv),

        "last2_diff": float(last - last_2) if n >= 2 else 0.0,
        "last3_diff": float(last - last_3) if n >= 3 else 0.0,
    }
    # Replace infinities
    for k, v in list(f.items()):
        if isinstance(v, float) and (not np.isfinite(v)):
            f[k] = 0.0
    return f


def load_scores(scores_path: str, single_user_id: Optional[str]) -> pd.DataFrame:
    df = pd.read_json(scores_path)
    _ensure_cols(df)
    if "user_id" not in df.columns:
        if not single_user_id:
            raise ValueError("scores JSON is missing user_id; provide --user-id for single-user files.")
        df["user_id"] = single_user_id
    df["date"] = pd.to_datetime(df["date"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["date", "score"])
    return df[["user_id", "date", "score"]]


def build_feature_table(scores_df: pd.DataFrame) -> pd.DataFrame:
    feats = []
    for uid, g in scores_df.groupby("user_id", sort=False):
        f = features_from_timeseries(g)
        f["user_id"] = uid
        feats.append(f)
    feat_df = pd.DataFrame(feats).set_index("user_id").sort_index()
    return feat_df.reset_index()


def maybe_train(feat_df: pd.DataFrame, labels_path: Optional[str], outdir: str) -> None:
    if not labels_path:
        print("No labels provided; skipping model training.")
        return
    labels = pd.read_json(labels_path)
    if "user_id" not in labels.columns or "close_to_burnout" not in labels.columns:
        raise ValueError("labels.json must have columns: user_id, close_to_burnout")

    data = feat_df.merge(labels, on="user_id", how="inner")
    if data["close_to_burnout"].nunique() < 2:
        print("Only one class present in labels after merge; cannot train a classifier.")
        return

    # Prepare features & groups
    X = data.drop(columns=["user_id", "close_to_burnout"])
    y = data["close_to_burnout"].astype(int).values
    groups = data["user_id"].values  # GroupKFold by user

    pipe = Pipeline([
        ("scaler", StandardScaler(with_mean=True, with_std=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    cv = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    scoring = {"roc_auc": "roc_auc", "pr_auc": "average_precision"}
    cv_res = cross_validate(pipe, X, y, groups=groups, cv=cv, scoring=scoring, return_estimator=True)
    mean_roc = float(np.mean(cv_res["test_roc_auc"]))
    mean_pr = float(np.mean(cv_res["test_pr_auc"]))

    # Fit final on all data
    pipe.fit(X, y)

    os.makedirs(outdir, exist_ok=True)
    joblib.dump(pipe, os.path.join(outdir, "model.pkl"))
    with open(os.path.join(outdir, "metrics.txt"), "w") as f:
        f.write(f"ROC-AUC (GroupKFold mean): {mean_roc:.4f}\n")
        f.write(f"PR-AUC  (GroupKFold mean): {mean_pr:.4f}\n")
        f.write("\nFeatures used:\n")
        for c in X.columns:
            f.write(f"- {c}\n")

    print(f"Saved model to {os.path.join(outdir, 'model.pkl')}")
    print(f"CV ROC-AUC: {mean_roc:.4f} | PR-AUC: {mean_pr:.4f}")
    print(f"Metrics written to {os.path.join(outdir, 'metrics.txt')}")


def main():
    ap = argparse.ArgumentParser(description="Extract time-series features from scores and train burnout risk model.")
    ap.add_argument("--scores", required=True, help="Path to scores.json (per-row: date, score, optional user_id).")
    ap.add_argument("--labels", required=False, help="Path to labels.json (per-row: user_id, close_to_burnout).")
    ap.add_argument("--outdir", required=True, help="Output directory for features and model.")
    ap.add_argument("--user-id", required=False, help="User id to assign if scores.json lacks user_id.")
    args = ap.parse_args()

    scores_df = load_scores(args.scores, args.user_id)
    feat_df = build_feature_table(scores_df)

    os.makedirs(args.outdir, exist_ok=True)
    feat_path = os.path.join(args.outdir, "features.csv")
    feat_df.to_csv(feat_path, index=False)
    print(f"Wrote features to {feat_path} (rows={len(feat_df)})")

    # Train if labels provided
    maybe_train(feat_df, args.labels, args.outdir)


if __name__ == "__main__":
    main()

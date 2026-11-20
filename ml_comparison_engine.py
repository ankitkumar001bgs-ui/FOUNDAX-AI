"""Reproducible educational ML comparison for the FOUNDAX synthetic footing dataset.

Never interprets predicted footing sizes as verified structural designs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

INPUTS = ["column_load_kN", "sbc_kN_m2"]
TARGETS = ["footing_length_m", "footing_breadth_m", "required_area_m2"]


def prepare_data(df: pd.DataFrame, target: str):
    if target not in TARGETS:
        raise ValueError("Unsupported prediction target")
    missing = [c for c in INPUTS + [target] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing dataset columns: {', '.join(missing)}")
    frame = df[INPUTS + [target]].apply(pd.to_numeric, errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    frame = frame[(frame[INPUTS] > 0).all(axis=1) & (frame[target] > 0)]
    if len(frame) < 50:
        raise ValueError("At least 50 valid rows are required")
    # Exclude other derived outputs from predictors to avoid target leakage.
    return frame[INPUTS], frame[target], len(df) - len(frame)


def evaluate_models(df: pd.DataFrame, target: str, test_fraction: float = 0.2, seed: int = 42, include_xgboost: bool = True):
    X, y, dropped = prepare_data(df, target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_fraction, random_state=seed)
    models = {
        "Linear Regression": make_pipeline(SimpleImputer(strategy="median"), LinearRegression()),
        "Random Forest": RandomForestRegressor(n_estimators=120, min_samples_leaf=2, random_state=seed, n_jobs=-1),
        "ANN (MLP)": make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(48, 24), max_iter=450, early_stopping=True, random_state=seed)),
    }
    notes = []
    if include_xgboost:
        try:
            from xgboost import XGBRegressor
            models["XGBoost"] = XGBRegressor(n_estimators=150, max_depth=4, learning_rate=0.06, subsample=0.9, colsample_bytree=1.0, objective="reg:squarederror", random_state=seed, n_jobs=2)
        except ImportError:
            notes.append("XGBoost unavailable: install optional package xgboost to compare it.")
    results = []
    predictions = pd.DataFrame({"Actual": y_test.to_numpy()}, index=y_test.index)
    importances = {}
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = np.asarray(model.predict(X_test), dtype=float)
            if not np.isfinite(y_pred).all():
                raise ValueError("Model returned non-finite predictions")
            results.append({"Model": name, "R²": float(r2_score(y_test, y_pred)), "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))), "MAE": float(mean_absolute_error(y_test, y_pred))})
            predictions[name] = y_pred
            perm = permutation_importance(model, X_test, y_test, scoring="neg_mean_absolute_error", n_repeats=3, random_state=seed)
            importances[name] = pd.DataFrame({"Feature": INPUTS, "MAE increase on permutation": perm.importances_mean}).sort_values("MAE increase on permutation", ascending=False)
        except Exception as exc:
            notes.append(f"{name} could not be evaluated: {type(exc).__name__}: {exc}")
    if not results:
        raise RuntimeError("No models completed evaluation")
    return {"metrics": pd.DataFrame(results).sort_values("RMSE").reset_index(drop=True), "predictions": predictions.reset_index(drop=True), "importance": importances, "train_count": len(X_train), "test_count": len(X_test), "dropped": dropped, "notes": notes}

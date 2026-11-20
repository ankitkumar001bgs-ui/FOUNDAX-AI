"""Five-fold reproducible synthetic-data validation and hand-formula baseline."""
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from ml_comparison_engine import prepare_data


def baseline_predict(X, target):
    area = X["column_load_kN"].to_numpy(dtype=float) / X["sbc_kN_m2"].to_numpy(dtype=float)
    if target == "required_area_m2":
        return area
    # Ideal square footing side; no thickness, reinforcement, settlement or load factors.
    return np.sqrt(area)


def run_cv(df, target, folds=5, seed=42, include_xgb=False):
    X, y, dropped = prepare_data(df, target)
    cv = KFold(n_splits=folds, shuffle=True, random_state=seed)
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=70, min_samples_leaf=2, random_state=seed, n_jobs=1),
        "ANN (MLP)": make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(32,16), max_iter=300, early_stopping=True, random_state=seed)),
    }
    notes=[]
    if include_xgb:
        try:
            from xgboost import XGBRegressor
            models["XGBoost"] = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.07, objective="reg:squarederror", random_state=seed, n_jobs=1)
        except ImportError:
            notes.append("XGBoost not installed; optional comparison skipped.")
    rows=[]
    for name, model in models.items():
        try:
            scores=cross_validate(model,X,y,cv=cv,scoring={"r2":"r2","mae":"neg_mean_absolute_error","mse":"neg_mean_squared_error"},n_jobs=1,error_score="raise")
            for fold in range(folds):
                rows.append({"Model":name,"Fold":fold+1,"R²":float(scores['test_r2'][fold]),"MAE":float(-scores['test_mae'][fold]),"RMSE":float(np.sqrt(-scores['test_mse'][fold]))})
        except Exception as e:
            notes.append(f"{name} failed: {type(e).__name__}: {e}")
    for fold,(_,test_idx) in enumerate(cv.split(X),1):
        truth=y.iloc[test_idx].to_numpy(dtype=float)
        pred=baseline_predict(X.iloc[test_idx],target)
        rows.append({"Model":"Conventional A=P/SBC baseline","Fold":fold,"R²":float(r2_score(truth,pred)),"MAE":float(mean_absolute_error(truth,pred)),"RMSE":float(np.sqrt(mean_squared_error(truth,pred)))})
    detail=pd.DataFrame(rows)
    if detail.empty: raise ValueError('No successful evaluations')
    summary=detail.groupby('Model',as_index=False).agg(R2_mean=('R²','mean'),R2_std=('R²','std'),RMSE_mean=('RMSE','mean'),RMSE_std=('RMSE','std'),MAE_mean=('MAE','mean'),MAE_std=('MAE','std')).sort_values('RMSE_mean')
    return {'folds':detail,'summary':summary,'valid_rows':len(X),'dropped':dropped,'notes':notes}

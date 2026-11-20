# FOUNDAX AI — Phase 5: ML Model Comparison & Validation

This package extends Phase 4, preserving the Welcome Page and existing modules.

## Added
- `pages/13_ML_Model_Comparison.py` — UI for training Linear Regression, Random Forest, XGBoost (if installed) and ANN (MLPRegressor) on the existing synthetic dataset.
- `ml_comparison_engine.py` — train/test split, R², RMSE, MAE, permutation feature importance, and downloadable test predictions.
- `requirements.txt` — dependency manifest (missing from earlier upgrade ZIPs).

## Run (Windows PowerShell, Python 3.13)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If you already have a working `.venv`, skip its creation and just install requirements.

## Scientific limitations
The 5,000-row dataset is synthetic and contains only column load and SBC as inputs; it cannot substantiate predictions based on material grades, column dimensions, or reinforcement. The benchmark uses a fixed held-out test split, not k-fold CV. It does not establish IS 456 compliance or real-building validation. Model training happens when the user clicks Train & Compare Models and may take time. XGBoost is optional in the page but included in requirements.

Do not push this package to the live website until the local app and new page work correctly.

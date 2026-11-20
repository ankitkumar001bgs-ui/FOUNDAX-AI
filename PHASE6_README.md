# FOUNDAX AI — College Proposal Phase 6

Added **Cross-Validation & Conventional Sizing Comparison** page and `cross_validation_engine.py`.

Run with Python 3.13:
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The app performs 3/5-fold cross-validation on the synthetic dataset and compares ML predictions to the idealized formula A=P/SBC (square side sqrt(A)). This is **not** comparison with a code-verified conventional footing design. No cost savings or real-building validation are claimed.

Only publish after testing. Preserve backup of the working live app.

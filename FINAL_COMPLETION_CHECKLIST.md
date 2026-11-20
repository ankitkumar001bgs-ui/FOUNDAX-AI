# FOUNDAX AI — Final verification checklist

This release retains the original dark theme, consolidated sidebar, existing ML/optimization and case-study pages, and adds an independent preliminary bearing benchmark in **Verification & Audit**.

## What has been tested in this release
- Python syntax compilation of all project Python files.
- Four deterministic tests for concentric pressure, eccentric pressure, contact failure and invalid inputs.

## Still required before claiming the college objectives are fully achieved
- Obtain a genuine building's load schedule, soil report, footing drawings and steel schedule. No genuine building data has been supplied.
- Check the isolated AND combined footing methods against hand calculations with documented design assumptions and the applicable IS codes.
- Verify flexure, one-way shear, punching shear, anchorage, development length, detailing, settlement, uplift, sliding and other relevant checks with a qualified engineer.
- Confirm optimization constraints and independently check that cost comparisons are between safe, equivalent alternatives. Existing Differential Evolution is a preliminary cost model only.
- Confirm the ML dataset provenance, held-out testing, cross-validation and error metrics, and distinguish synthetic from real-building validation.
- Check actual deployment logs and functionality on Streamlit Cloud.

**Do not use the application to authorize construction.**

## Running
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

To update an existing GitHub clone, copy the package's source files into that clone, **excluding `.venv`, `__pycache__`, and `.git`**, then inspect `git status` and commit/push only intended changes.

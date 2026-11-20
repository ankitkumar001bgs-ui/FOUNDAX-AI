# FOUNDAX AI — Phase 7

Adds `pages/15_Real_Building_Validation_Cost.py` and `case_study_validation_engine.py` to Phase 6. Existing modules, ML dataset/model and Welcome screen are preserved.

## Features
- Actual building evidence/reference fields, editable multi-footing schedule, CSV upload/template.
- Comparison of entered drawing footing area/pressure with an illustrative concentric-load square-footing area.
- Concrete/excavation quantities and **partial** cost comparison (steel/formwork/labor excluded).
- CSV results and a PDF case-study worksheet with explicit assumptions and unverified status.
- Evidence completeness warnings and no claim of actual cost savings or construction-ready design.

## Run (Windows PowerShell)
```
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Tests
`python -m unittest discover -s tests -v`

## Important
Pre-filled examples are fictional. A real case study requires actual building data and supporting reports. Entered reference strings are not authenticated. This page does not certify IS 456 compliance or complete structural design. Do not publish to the live app before local testing.

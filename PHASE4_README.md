# FOUNDAX AI Phase 4 — Reinforcement & Capacity Screening

New: `capacity_screening.py` and `pages/12_Reinforcement_Capacity_Screening.py`, linked from `app.py`.

The page provides **illustrative** reinforcement-area demand, supplied reinforcement per metre, singly reinforced flexural resistance, one-way and punching shear stress demand, and comparison to **user-entered independently verified allowable limits**. It is not a complete IS 456 structural design or construction document. The input example is fictional.

## Install and run
1. Extract ZIP to a new folder.
2. Copy `requirements.txt` from your current *working* FOUNDAX-AI folder (this archive intentionally has no requirements.txt because the original supplied project did not include one).
3. In PowerShell inside the extracted folder: `py -3.13 -m venv .venv` then `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe -m streamlit run app.py`.
4. Test Welcome, existing modules, and Reinforcement & Capacity Screening.

## Engineering caveats
User must independently verify tau_one, tau_punch and x_u/d limits from appropriate IS code provisions. Defaults are *not* verified values. This module does not check minimum reinforcement, development length, spacing limits, settlement, eccentric loads, geotechnical bearing, detailing, column-footing force transfer, or full load combinations. All output is screening only, not approval.

## Validation
Python syntax compilation and simple function checks completed. Full local Streamlit runtime and independent hand-calculation verification pending. Do not push to live app until local test passes.

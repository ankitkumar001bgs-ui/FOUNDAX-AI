# FOUNDAX AI — Phase 3: Structural Demand Worksheet

## What changed
- Added `pages/11_Structural_Demand_Worksheet.py`, linked in `app.py`.
- Calculates illustrative factored bending, one-way shear and punching shear **actions**, with input validation, multiple-footing editable schedule and CSV export.
- Checks a simple consistency condition between entered factored P and entered uniform factored q; mismatches are flagged for review.
- Corrected the Phase 2 navigation defect: exactly one default page depending on welcome/start state, and only welcome page registered until started.

## Limitations
- **No structural capacities or reinforcement design are computed.** Not a construction-ready footing design or proof of IS Code compliance.
- Applies only to concentric, centrally loaded, rigid rectangular isolated pads with full contact and independently verified uniform factored soil pressure. Eccentric, combined, boundary or uplift conditions are excluded.
- Fictional sample rows are not real-building evidence. Real case study needs drawings, geotechnical report, independently checked calculations and engineer review.

## Test
1. Extract ZIP into a separate test folder.
2. Create Python 3.13 venv and install your dependencies (copy verified requirements from your working project if absent).
3. Run `python -m streamlit run app.py` with the venv interpreter.
4. Test welcome button, home/sidebar, case-study pages, new worksheet, CSV template and export.
5. Do not replace production app until local tests pass. Do not commit `.venv`.

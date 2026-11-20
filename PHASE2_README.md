# FOUNDAX AI — Phase 2: Eccentric Bearing Screening

## Changes
- Adds `pages/10_Eccentric_Bearing_Screening.py` and registers it in `app.py`.
- User-editable multiple footing service loads, dimensions, Mx/My, soil bearing pressure and source reference.
- CSV import, blank template, screening table, CSV export.
- Full-contact linear soil pressure screening with clear out-of-scope warnings.
- Existing welcome screen, ML and other modules preserved.

## Limitations
- **Not full footing structural design** and not proof of IS-code compliance.
- A negative calculated corner pressure means loss of full contact; the tool does not compute reduced contact area.
- Assumes rigid rectangular footing, vertical service load, linear pressure distribution, and compatible allowable bearing pressure basis.
- Does not check settlement, lateral actions, load combinations, shear, flexure, reinforcement, stability or group interaction.
- Example inputs are fictional, not an actual case study.

## Local test
1. Extract to a NEW folder; do not overwrite your live-working folder.
2. Run `.\.venv\Scripts\python.exe -m streamlit run app.py` from that folder (create environment and install requirements if needed).
3. Test Welcome, Home, Real Building Case Study and Eccentric Bearing Screening.
4. Only merge into production after review and testing.

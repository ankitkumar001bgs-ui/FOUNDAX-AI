# FOUNDAX AI — Consolidated Review Build

## What changed
- Six grouped sidebar workspaces replace sixteen individual module links.
- Every original module remains available through a **Choose a tool** dropdown inside its workspace.
- Welcome screen, original engines, case-study inputs and cost worksheets remain.
- Added a project audit and case-study evidence checklist with TXT export.
- Removed duplicate `st.set_page_config` calls in child pages to ensure single app configuration.

## Run locally (Windows PowerShell)
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Not yet complete / important limitations
This is a **consolidated review build**, not a construction-ready or fully verified structural design application. Actual building data, verified IS 456 and geotechnical checks, independent manual/software comparisons and complete UI testing are pending. Existing ML metrics use synthetic training data. Do not present the optimization's cost differences as validated engineering savings.

## Testing
Python syntax compilation and selected engine tests are performed in the build environment. Full Streamlit browser workflows require local testing before GitHub deployment.

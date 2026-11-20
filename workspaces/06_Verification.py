from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Verification & Project Audit')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'Validation & Testing': '5_Validation_and_Testing.py', 'Project Audit': '_project_audit.py', 'Independent Bearing Benchmark': '17_Independent_Bearing_Benchmark.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_06_Verification.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

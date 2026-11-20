from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Building Case Study')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'Building Data Entry': '9_Real_Building_Case_Study.py', 'Drawing & Cost Comparison': '15_Real_Building_Validation_Cost.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_04_Case_Study.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Reports & Drawings')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'Engineering PDF': '7_Engineering_Report.py', 'Drawing Generator': '8_Footing_Drawing_Generator.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_05_Reports.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

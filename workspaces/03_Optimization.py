from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Cost & Optimization')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'Cost Optimization': '4_Cost_Optimization.py', 'Full Cost Worksheet': '16_Case_Study_Evidence_Full_Cost.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_03_Optimization.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

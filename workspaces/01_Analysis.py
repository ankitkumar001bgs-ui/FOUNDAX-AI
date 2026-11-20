from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Footing Analysis')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'Isolated Footing': '2_Isolated_Footing_Analysis.py', 'Combined Footing': '6_Combined_Footing_Analysis.py', 'Eccentric Bearing': '10_Eccentric_Bearing_Screening.py', 'Structural Demand': '11_Structural_Demand_Worksheet.py', 'Reinforcement Screening': '12_Reinforcement_Capacity_Screening.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_01_Analysis.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

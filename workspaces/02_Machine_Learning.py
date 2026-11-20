from pathlib import Path
import runpy
import streamlit as st
ROOT = Path(__file__).resolve().parent.parent
st.title('Machine Learning')
st.caption("Select a tool below. Only the selected tool runs, keeping the sidebar clean.")
OPTIONS = {'ML Prediction': '3_ML_Prediction.py', 'Model Comparison': '13_ML_Model_Comparison.py', 'Cross-Validation': '14_Cross_Validation_Conventional_Comparison.py'}
choice = st.selectbox("Choose a tool", list(OPTIONS), key="group_02_Machine_Learning.py")
target = OPTIONS[choice]
folder = "workspaces" if target.startswith("_") else "pages"
runpy.run_path(str(ROOT / folder / target), run_name="__main__")

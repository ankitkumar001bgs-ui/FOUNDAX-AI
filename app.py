from pathlib import Path
import streamlit as st
from theme import apply_theme

st.set_page_config(
    page_title=" | Home",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"

MODULES = [
    ("Project Overview", "1_Project_Overview.py", "Project background, objectives and methodology"),
    ("Isolated Footing Analysis", "2_Isolated_Footing_Analysis.py", "Preliminary area sizing and structural demands"),
    ("ML Prediction", "3_ML_Prediction.py", "Random Forest prediction and synthetic-data test metrics"),
    ("Cost Optimization", "4_Cost_Optimization.py", "Illustrative cost model and Differential Evolution"),
    ("Validation and Testing", "5_Validation_and_Testing.py", "Automated tests, evaluation and limitations"),
    ("Combined Footing Analysis", "6_Combined_Footing_Analysis.py", "Two-column geometry and idealized bearing pressures"),
    ("Engineering PDF Report", "7_Engineering_Report.py", "Downloadable preliminary isolated footing calculations"),
]

st.title("FOUNDAX AI")
st.subheader("ML-Based Prediction and Preliminary Optimization of Footing Design")
st.write(
    "An educational civil engineering software prototype integrating "
    "preliminary footing calculations, machine learning, numerical cost "
    "optimization, automated testing and calculation reporting."
)
st.warning(
    "Educational prototype only. Structural capacity, settlement, reinforcement "
    "detailing and full code compliance have not been established. "
    "Do not use outputs for construction."
)

st.divider()
st.header("Project Workflow")
st.write(
    "**Inputs → Preliminary Analysis → ML Prediction → Cost Optimization "
    "→ Validation & Testing → PDF Report**"
)

st.header("Project Modules")
for name, filename, description in MODULES:
    path = PAGES / filename
    with st.container(border=True):
        st.markdown(f"**{name}**")
        st.caption(description)
        if path.is_file():
            st.page_link(f"pages/{filename}", label=f"Open {name}")
        else:
            st.info(
                f"Page not found: pages/{filename}. "
                "Check the file location and spelling in VS Code."
            )

st.divider()
st.header("Technology Stack")
st.write(
    "**Python** · **Streamlit** · **pandas / NumPy** · "
    "**scikit-learn (Random Forest)** · **SciPy (Differential Evolution)** "
    "· **ReportLab**"
)

st.header("Current Validation Status")
st.write(
    "Software arithmetic tests and held-out evaluation on synthetic records "
    "are implemented. Independent engineering validation is still pending."
)
st.caption(
    "The ML dataset was generated from a preliminary sizing formula; "
    "high prediction accuracy does not prove real-world structural safety."
)

st.sidebar.title("FOUNDAX AI")
st.sidebar.caption("Select a page from the Streamlit navigation menu.")
st.sidebar.divider()
st.sidebar.caption("Preliminary engineering research prototype")

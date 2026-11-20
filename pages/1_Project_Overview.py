from formula_reference_guide import show_reference_guide

import streamlit as st

st.set_page_config(
    page_title="FOUNDAX AI | Project Overview",
    layout="wide"
)

st.title("FOUNDAX AI")
st.subheader(
    "ML-Based Prediction and Preliminary "
    "Optimization of Footing Design"
)

st.divider()

st.header("1. Project Introduction")

st.write(
    "FOUNDAX AI is an educational civil engineering "
    "software prototype combining preliminary footing "
    "calculations, machine learning and numerical "
    "cost optimization."
)

st.header("2. Project Objectives")

st.markdown("""
1. Calculate preliminary isolated footing dimensions.
2. Analyze preliminary combined footing geometry.
3. Predict isolated footing size using Random Forest.
4. Compare illustrative construction costs.
5. Apply Differential Evolution for cost minimization.
6. Evaluate numerical calculations and ML performance.
7. Generate downloadable engineering reports.
""")

st.header("3. Project Workflow")

st.code(
    "Input Parameters\n"
    "       |\n"
    "       v\n"
    "Preliminary Footing Analysis\n"
    "       |\n"
    "       v\n"
    "Machine Learning Prediction\n"
    "       |\n"
    "       v\n"
    "Cost Optimization\n"
    "       |\n"
    "       v\n"
    "Validation and Testing\n"
    "       |\n"
    "       v\n"
    "Engineering Calculation Report",
    language="text"
)

st.header("4. Technology Stack")

st.write(
    "Python | Streamlit | Pandas | NumPy | "
    "Scikit-learn | SciPy | ReportLab"
)

st.header("5. Current Limitations")

st.warning(
    "The ML dataset is synthetic and based on a "
    "preliminary sizing formula. Structural capacity, "
    "reinforcement detailing, settlement and full "
    "engineering-code compliance are not verified. "
    "The software must not be used for construction."
)


# Educational glossary and standards (does not alter calculations)
show_reference_guide("overview")

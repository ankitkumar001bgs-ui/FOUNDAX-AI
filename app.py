
from pathlib import Path
import streamlit as st
from theme import apply_theme

# ==========================================
# FOUNDAX AI - Application Configuration
# ==========================================

st.set_page_config(
    page_title="FOUNDAX AI | Home",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"

# ==========================================
# Project Modules
# ==========================================

MODULES = [
    (
        "Project Overview",
        "1_Project_Overview.py",
        "Project background, objectives and methodology",
    ),
    (
        "Isolated Footing Analysis",
        "2_Isolated_Footing_Analysis.py",
        "Preliminary area sizing and structural demands",
    ),
    (
        "ML Prediction",
        "3_ML_Prediction.py",
        "Random Forest prediction and synthetic-data test metrics",
    ),
    (
        "Cost Optimization",
        "4_Cost_Optimization.py",
        "Illustrative cost model and Differential Evolution",
    ),
    (
        "Validation and Testing",
        "5_Validation_and_Testing.py",
        "Automated tests, evaluation and limitations",
    ),
    (
        "Combined Footing Analysis",
        "6_Combined_Footing_Analysis.py",
        "Two-column geometry and idealized bearing pressures",
    ),
    (
        "Engineering PDF Report",
        "7_Engineering_Report.py",
        "Downloadable preliminary isolated footing calculations",
    ),
    (
        "Footing Drawing Generator",
        "8_Footing_Drawing_Generator.py",
        "2D plan, section and interactive 3D reinforcement",
    ),
]

# ==========================================
# Register Available Pages
# ==========================================

registered_pages = {}

for name, filename, description in MODULES:
    page_path = PAGES / filename

    if page_path.is_file():
        registered_pages[filename] = st.Page(
            f"pages/{filename}",
            title=name,
            help=description,
        )

# ==========================================
# Home Dashboard
# ==========================================

def home():

    st.title("FOUNDAX AI")

    st.subheader(
        "ML-Based Prediction and Preliminary "
        "Optimization of Footing Design"
    )

    st.write(
        "An educational civil engineering software prototype "
        "integrating preliminary footing calculations, machine "
        "learning, numerical cost optimization, automated testing "
        "and calculation reporting."
    )

    st.warning(
        "Educational prototype only. Structural capacity, "
        "settlement, reinforcement detailing and full code "
        "compliance have not been established. "
        "Do not use outputs for construction."
    )

    st.divider()

    # Project Workflow

    st.header("Project Workflow")

    st.write(
        "**Inputs → Preliminary Analysis → ML Prediction "
        "→ Cost Optimization → Validation & Testing "
        "→ PDF Report**"
    )

    # Project Modules

    st.header("Project Modules")

    for name, filename, description in MODULES:

        with st.container(border=True):

            st.markdown(f"**{name}**")

            st.caption(description)

            page = registered_pages.get(filename)

            if page is not None:

                st.page_link(
                    page,
                    label=f"Open {name}",
                )

            else:

                st.info(
                    f"Page not found: pages/{filename}. "
                    "Check the file location and spelling in GitHub."
                )

    st.divider()

    # Technology Stack

    st.header("Technology Stack")

    st.write(
        "**Python** · **Streamlit** · **pandas / NumPy** · "
        "**scikit-learn (Random Forest)** · "
        "**SciPy (Differential Evolution)** · "
        "**ReportLab**"
    )


# ==========================================
# Welcome Screen (shown first in each new session)
# ==========================================

def welcome():
    st.markdown("<div style='height: 7vh'></div>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 2.5, 1])
    with center:
        st.markdown(
            """<div style="text-align:center;padding:28px 10px 20px;">
              <p style="font-size:14px;letter-spacing:3px;font-weight:700;color:#0d9488;">
                CIVIL ENGINEERING · INTELLIGENT DESIGN</p>
              <h1 style="font-size:clamp(42px,6vw,76px);line-height:1.12;
                  margin:12px 0 18px;"> FOUNDAX AI</h1>
              <p style="font-size:clamp(17px,2vw,23px);line-height:1.5;">
                ML-Based Prediction &amp; Preliminary Optimization<br>of Footing Design</p>
              <div style="height:4px;width:90px;background:#0d9488;
                  margin:28px auto;border-radius:20px;"></div>
              <p style="font-size:18px;font-weight:700;">Government Engineering College Khagaria</p>
              <p style="font-size:15px;opacity:.85;">Session 2023–2027 · Guided by Dr. Irfan Ansari</p>
            </div>""",
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("🚀 Let's Get Started →", type="primary", use_container_width=True):
            st.session_state["foundax_started"] = True
            st.rerun()
        st.caption("Educational prototype · Preliminary results only · Not for construction")


# ==========================================
# Navigation: show ONLY welcome until button is clicked
# ==========================================

if not st.session_state.get("foundax_started", False):
    welcome_page = st.Page(welcome, title="Welcome", default=True)
    selected_page = st.navigation([welcome_page], position="hidden")
else:
    home_page = st.Page(home, title="Home", default=True)
    navigation_sections = {"Home": [home_page]}
    if registered_pages:
        navigation_sections["Project Modules"] = list(registered_pages.values())
    selected_page = st.navigation(
        navigation_sections,
        position="sidebar",
        expanded=True,
    )

selected_page.run()


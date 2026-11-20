
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
# Consolidated navigation: 6 workspaces instead of 16 sidebar pages
# ==========================================
GROUPS = [
    ("Footing Analysis", "01_Analysis.py", "Isolated, combined, bearing and structural screening"),
    ("Machine Learning", "02_Machine_Learning.py", "Prediction, comparison and cross-validation"),
    ("Cost & Optimization", "03_Optimization.py", "Optimization and complete cost worksheet"),
    ("Building Case Study", "04_Case_Study.py", "Actual building inputs and drawing comparison"),
    ("Reports & Drawings", "05_Reports.py", "Engineering reports and footing drawings"),
    ("Verification & Audit", "06_Verification.py", "Testing, evidence and submission readiness"),
]
registered_pages = {filename: st.Page(f"workspaces/{filename}", title=name, help=description) for name,filename,description in GROUPS}
MODULES = GROUPS

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
                    f"Page not found: workspaces/{filename}. "
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
# Welcome / Intro Screen
# ==========================================

def welcome():
    st.markdown("<div style='height: 5vh'></div>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 2.4, 1])
    with center:
        st.markdown(
            """<div style="text-align:center; padding: 38px 20px 18px;">
                <div style="font-size:16px;letter-spacing:4px;color:#0f766e;font-weight:700;">
                    CIVIL ENGINEERING · INTELLIGENT DESIGN
                </div>
                <div style="font-size:clamp(46px,7vw,78px);font-weight:800;letter-spacing:-2px;
                            line-height:1.2;margin:20px 0 8px;">FOUNDAX AI</div>
                <div style="font-size:clamp(17px,2.3vw,24px);font-weight:500;line-height:1.5;
                            opacity:.86;margin:12px 0 30px;">
                    ML-Based Prediction &amp; Preliminary Optimization<br>of Footing Design
                </div>
                <div style="height:4px;width:92px;background:#0d9488;margin:0 auto 28px;
                            border-radius:20px;"></div>
                <div style="font-size:17px;font-weight:700;">Government Engineering College Khagaria</div>
                <div style="font-size:15px;opacity:.8;margin-top:9px;">
                    Session: 2023–2027 &nbsp; | &nbsp; Guided by: Dr. Irfan Ansari
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        if st.button("Let's Get Started", type="primary", use_container_width=True):
            st.session_state["foundax_started"] = True
            st.switch_page(home_page)
        st.caption("Educational prototype • Preliminary results only • Not for construction")


# ==========================================
# Navigation Setup
# ==========================================

home_page = st.Page(
    home,
    title="Home",
    default=st.session_state.get("foundax_started", False),
)

welcome_page = st.Page(
    welcome,
    title="Welcome",
    default=not st.session_state.get("foundax_started", False),
)

navigation_sections = ({"Home": [home_page]} if st.session_state.get("foundax_started", False) else {"Welcome": [welcome_page]})

if registered_pages and st.session_state.get("foundax_started", False):
    navigation_sections["Project Modules"] = list(
        registered_pages.values()
    )

# ==========================================
# Run Selected Page
# ==========================================

selected_page = st.navigation(
    navigation_sections,
    position="sidebar" if st.session_state.get("foundax_started", False) else "hidden",
    expanded=True,
)

selected_page.run()


from pathlib import Path
import streamlit as st

def apply_theme():
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"

    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


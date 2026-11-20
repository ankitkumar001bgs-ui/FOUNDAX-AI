"""Educational formula legend and reference notes for FOUNDAX AI.

References identify relevant standards, NOT a certification of compliance.
Exact subclauses must be checked against licensed/current standard copies.
"""
import streamlit as st

LEGENDS = {
    "isolated": [
        ("P", "Applied column/service vertical load", "kN"),
        ("q_allow", "Allowable soil bearing pressure (SBC input)", "kN/m²"),
        ("A_req", "Preliminary required plan area, P/q_allow", "m²"),
        ("B", "Square footing side length", "m"),
        ("c", "Square column side dimension", "m"),
        ("q_s", "Average service bearing pressure, P/B²", "kN/m²"),
        ("γ", "Assumed load factor (user input, not automatic code design)", "dimensionless"),
        ("q_u", "Assumed factored pressure, γP/B²", "kN/m²"),
        ("a", "Column-face to footing-edge projection, (B−c)/2", "m"),
        ("d", "Effective depth used for illustrative shear demand", "m"),
        ("M_u", "Simplified bending moment demand per metre width", "kN·m/m"),
        ("V_u", "Simplified one-way shear demand per metre width", "kN/m"),
        ("b_0", "Illustrative punching critical perimeter, 4(c+d)", "m"),
        ("V_p", "Simplified punching shear force demand", "kN"),
    ],
    "ml": [
        ("P", "Column/service load (model input)", "kN"),
        ("q_allow", "Allowable bearing pressure / SBC (model input)", "kN/m²"),
        ("A_req", "Analytical preliminary area, P/q_allow", "m²"),
        ("B", "Analytical square footing side, √A_req", "m"),
        ("y", "Actual/target value in model evaluation", "varies"),
        ("ŷ", "Machine-learning predicted value", "varies"),
        ("MAE", "Mean absolute error", "same as target"),
        ("RMSE", "Root mean squared error", "same as target"),
        ("R²", "Coefficient of determination (model score)", "dimensionless"),
    ],
    "cost": [
        ("x = [B,D]", "Optimization decision variables: footing side and thickness", "m"),
        ("B", "Square footing side length", "m"),
        ("D", "Assumed overall footing thickness", "m"),
        ("P", "Applied load", "kN"),
        ("q_allow", "Allowable bearing pressure", "kN/m²"),
        ("V_c = B²D", "Concrete volume", "m³"),
        ("ρ_s", "Assumed steel quantity per unit concrete volume; not reinforcement design", "kg/m³"),
        ("W_s = V_cρ_s", "Estimated steel mass", "kg"),
        ("H_e", "Assumed excavation depth", "m"),
        ("V_e = B²H_e", "Estimated excavation volume", "m³"),
        ("R_c", "Unit concrete rate", "currency/m³"),
        ("R_s", "Unit steel rate", "currency/kg"),
        ("R_e", "Unit excavation rate", "currency/m³"),
        ("C_c, C_s, C_e", "Concrete, steel and excavation costs", "currency"),
        ("C_total", "Sum of estimated component costs", "currency"),
    ],
    "combined": [
        ("P₁, P₂", "Service loads on columns 1 and 2", "kN"),
        ("P", "Total service load, P₁+P₂", "kN"),
        ("S", "Column centre-to-centre spacing", "m"),
        ("a", "Distance of first column centre from left footing edge", "m"),
        ("x_R", "Load resultant position from left edge", "m"),
        ("L", "Adopted combined footing length", "m"),
        ("B", "Adopted combined footing width", "m"),
        ("A_req", "Preliminary required area, P/q_allow", "m²"),
        ("q_avg", "Average bearing pressure, P/(LB)", "kN/m²"),
        ("e", "Longitudinal eccentricity, x_R−L/2", "m"),
        ("q_left, q_right", "Simplified linear edge pressures (full-contact assumption)", "kN/m²"),
    ],
    "report": [],
    "drawing": [
        ("B, L", "Footing plan width and length", "m or mm as displayed"),
        ("D", "Footing thickness", "m or mm as displayed"),
        ("c", "Column dimension", "m or mm as displayed"),
        ("d", "Effective depth (if calculated)", "m or mm as displayed"),
        ("Ø", "Nominal reinforcing bar diameter", "mm"),
        ("c/c", "Centre-to-centre reinforcement spacing", "mm"),
    ],
}
LEGENDS["report"] = LEGENDS["isolated"]

def show_reference_guide(section: str) -> None:
    """Display a non-intrusive expandable educational explanation."""
    with st.expander("📘 Formula symbols, units & relevant IS Code references", expanded=False):
        st.markdown("**Symbols used in this module**")
        st.table([
            {"Symbol / Term": symbol, "Meaning": meaning, "Unit": unit}
            for symbol, meaning, unit in LEGENDS.get(section, [])
        ])
        st.markdown("**Standards and source of methods**")
        if section in ("isolated", "combined", "report", "drawing"):
            st.markdown(
                "- **IS 456:2000, Clause 34 (Footings)** — relevant RCC footing design "
                "framework. The displayed demand calculations are simplified; full "
                "bending, shear, development length and detailing checks are **not verified**.\n"
                "- **IS 1904:1986** — general requirements for design and construction "
                "of foundations in soils; relevant background, **not implemented as a full check**.\n"
                "- **IS 6403:1981** — method for determining bearing capacity of shallow "
                "foundations; the app **takes allowable SBC as an input**, and does not "
                "calculate bearing capacity using this standard."
            )
        elif section == "cost":
            st.markdown(
                "- **IS 456:2000, Clause 34** — relevant to RCC footing checks, "
                "**not enforced by this simplified cost optimizer**.\n"
                "- **IS 1904:1986 / IS 6403:1981** — foundation and soil-bearing "
                "context; SBC is supplied as input.\n"
                "- **Differential Evolution** is a numerical optimization method, "
                "**not an IS Code design procedure**. Material rates and steel factor "
                "are illustrative assumptions."
            )
        elif section == "ml":
            st.markdown(
                "- **Random Forest, MAE, RMSE and R²** are machine-learning/statistical "
                "methods, **not formulas prescribed by IS 456**.\n"
                "- **IS 456:2000, Clause 34** is relevant to later RCC footing design "
                "checks, which this prediction does **not** establish.\n"
                "- **IS 6403:1981** concerns bearing capacity; here SBC is an input."
            )
        elif section == "validation":
            st.markdown(
                "- Software arithmetic tests and model metrics are **not equivalent "
                "to IS Code compliance**.\n"
                "- **IS 456:2000, Clause 34** is relevant to RCC footing verification; "
                "a complete code-compliance check is not implemented."
            )
        else:
            st.markdown(
                "- **IS 456:2000, Clause 34** — relevant footing design context.\n"
                "- **IS 1904:1986** — general foundation requirements.\n"
                "- **IS 6403:1981** — bearing-capacity context, not calculated here."
            )
        st.caption(
            "Reference status: contextual / educational, not verified compliance. "
            "Specific subclauses, code editions and applicability must be checked "
            "against the official standards before citing them as design authority. "
            "Do not use these preliminary results for construction."
        )

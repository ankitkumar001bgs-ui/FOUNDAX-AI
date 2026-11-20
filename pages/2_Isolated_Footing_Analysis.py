
import math
import pandas as pd
import streamlit as st

st.title("Isolated Footing Analysis")
from formula_reference_guide import show_reference_guide
show_reference_guide("isolated")

st.write(
    "Preliminary analysis of a centrally loaded "
    "square isolated footing."
)

st.caption(
    "Educational calculation module | "
    "Not a construction-ready structural design"
)

st.divider()

# ==========================================
# 1. INPUT PARAMETERS
# ==========================================

st.header("1. Input Parameters")

st.write(
    "Enter the service load, allowable soil bearing "
    "pressure, column dimensions and assumed "
    "footing properties."
)

with st.form("isolated_footing_analysis_form"):

    c1, c2 = st.columns(2)

    with c1:
        load = st.number_input(
            "Column Service Load, P (kN)",
            min_value=1.0,
            value=1000.0,
            step=50.0
        )

        sbc = st.number_input(
            "Allowable Soil Bearing Pressure (kN/m²)",
            min_value=1.0,
            value=200.0,
            step=10.0
        )

        column_width = st.number_input(
            "Square Column Width, c (m)",
            min_value=0.1,
            value=0.4,
            step=0.05
        )

    with c2:
        overall_depth = st.number_input(
            "Assumed Overall Footing Depth, D (m)",
            min_value=0.1,
            value=0.5,
            step=0.05
        )

        effective_depth = st.number_input(
            "Assumed Effective Depth, d (m)",
            min_value=0.05,
            value=0.42,
            step=0.01
        )

        load_factor = st.number_input(
            "Assumed Load Multiplier",
            min_value=1.0,
            value=1.5,
            step=0.1
        )

    calculate = st.form_submit_button(
        "Calculate Preliminary Footing Analysis"
    )

if calculate:

    if effective_depth >= overall_depth:
        st.error(
            "Effective depth must be smaller than "
            "the overall footing depth."
        )
        st.stop()

    # ======================================
    # 2. PRELIMINARY GEOMETRY
    # ======================================

    required_area = load / sbc

    theoretical_side = math.sqrt(required_area)

    adopted_side = (
        math.ceil(theoretical_side * 10 - 1e-10) / 10
    )

    provided_area = adopted_side ** 2

    if column_width >= adopted_side:
        st.error(
            "Column width must be smaller than "
            "the adopted footing side."
        )
        st.stop()

    # ======================================
    # 3. PRESSURE CALCULATIONS
    # ======================================

    service_pressure = load / provided_area

    assumed_factored_load = load * load_factor

    assumed_factored_pressure = (
        assumed_factored_load / provided_area
    )

    projection = (
        adopted_side - column_width
    ) / 2

    # ======================================
    # 4. SIMPLIFIED STRUCTURAL DEMANDS
    # ======================================

    bending_moment = (
        assumed_factored_pressure
        * projection ** 2 / 2
    )

    shear_distance = max(
        projection - effective_depth, 0
    )

    one_way_shear = (
        assumed_factored_pressure
        * shear_distance
    )

    critical_side = (
        column_width + effective_depth
    )

    punching_perimeter = (
        4 * critical_side
    )

    punching_applicable = (
        critical_side < adopted_side
    )

    if punching_applicable:
        punching_force = (
            assumed_factored_pressure
            * (
                provided_area
                - critical_side ** 2
            )
        )
    else:
        punching_force = None

    # ======================================
    # 5. RESULTS
    # ======================================

    st.header("2. Preliminary Sizing Results")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Required Plan Area",
        f"{required_area:.3f} m²"
    )

    r2.metric(
        "Adopted Footing Side",
        f"{adopted_side:.2f} m"
    )

    r3.metric(
        "Provided Plan Area",
        f"{provided_area:.3f} m²"
    )

    st.subheader("2.1 Geometry Summary")

    geometry_df = pd.DataFrame({
        "Parameter": [
            "Footing Type",
            "Footing Length",
            "Footing Width",
            "Column Width",
            "Assumed Overall Depth",
            "Assumed Effective Depth",
            "Column-to-Edge Projection"
        ],
        "Value": [
            "Square Isolated",
            f"{adopted_side:.2f} m",
            f"{adopted_side:.2f} m",
            f"{column_width:.2f} m",
            f"{overall_depth:.2f} m",
            f"{effective_depth:.2f} m",
            f"{projection:.3f} m"
        ]
    })

    st.dataframe(
        geometry_df,
        hide_index=True,
        use_container_width=True
    )

    # ======================================
    # 6. STEP-BY-STEP FORMULAS
    # ======================================

    st.header("3. Engineering Formulas and Calculations")

    st.subheader("3.1 Required Footing Area")

    st.latex(
        r"A_{req} = \frac{P}{q_{allow}}"
    )

    st.latex(
        rf"A_{{req}} = "
        rf"\frac{{{load:.2f}}}{{{sbc:.2f}}}"
        rf" = {required_area:.3f}\ \mathrm{{m^2}}"
    )

    st.write(
        "The required area is estimated by dividing "
        "the applied column service load by the "
        "entered allowable bearing pressure."
    )

    st.subheader("3.2 Square Footing Side")

    st.latex(
        r"B = \sqrt{A_{req}}"
    )

    st.latex(
        rf"B = \sqrt{{{required_area:.3f}}}"
        rf" = {theoretical_side:.3f}\ \mathrm{{m}}"
    )

    st.write(
        f"Adopted side length = {adopted_side:.2f} m, "
        "rounded upward to the next 0.1 m."
    )

    st.subheader("3.3 Average Service Bearing Pressure")

    st.latex(
        r"q_s = \frac{P}{B^2}"
    )

    st.latex(
        rf"q_s = \frac{{{load:.2f}}}"
        rf"{{{provided_area:.3f}}}"
        rf" = {service_pressure:.3f}"
        rf"\ \mathrm{{kN/m^2}}"
    )

    st.write(
        "This is the simplified average bearing "
        "pressure from the column service load only."
    )

    if service_pressure <= sbc + 1e-8:
        st.success(
            "The calculated average service pressure "
            "does not exceed the entered allowable "
            "bearing pressure under these assumptions."
        )
    else:
        st.error(
            "The calculated average service pressure "
            "exceeds the entered allowable value."
        )

    st.subheader("3.4 Assumed Factored Pressure")

    st.latex(
        r"q_u = \frac{\gamma P}{B^2}"
    )

    st.latex(
        rf"q_u = \frac{{{load_factor:.2f}"
        rf"\times {load:.2f}}}"
        rf"{{{provided_area:.3f}}}"
        rf" = {assumed_factored_pressure:.3f}"
        rf"\ \mathrm{{kN/m^2}}"
    )

    st.write(
        "The load multiplier is an illustrative input. "
        "This is not a verified code load combination."
    )

    st.subheader("3.5 Column-to-Edge Projection")

    st.latex(
        r"a = \frac{B-c}{2}"
    )

    st.latex(
        rf"a = \frac{{{adopted_side:.2f}"
        rf"-{column_width:.2f}}}{{2}}"
        rf" = {projection:.3f}\ \mathrm{{m}}"
    )

    st.subheader("3.6 Simplified Bending Moment Demand")

    st.latex(
        r"M_u = \frac{q_u a^2}{2}"
    )

    st.latex(
        rf"M_u = \frac{{{assumed_factored_pressure:.3f}"
        rf"\times {projection:.3f}^2}}{{2}}"
        rf" = {bending_moment:.3f}"
        rf"\ \mathrm{{kN\,m/m}}"
    )

    st.write(
        "This expression estimates cantilever bending "
        "demand per metre width for the assumed "
        "uniform pressure distribution."
    )

    st.subheader("3.7 Simplified One-Way Shear Demand")

    st.latex(
        r"V_u = q_u \max(a-d,0)"
    )

    st.latex(
        rf"V_u = {assumed_factored_pressure:.3f}"
        rf"\times {shear_distance:.3f}"
        rf" = {one_way_shear:.3f}"
        rf"\ \mathrm{{kN/m}}"
    )

    st.write(
        "This is a simplified shear-force demand "
        "per metre width, not a shear-capacity check."
    )

    st.subheader("3.8 Simplified Punching Shear Demand")

    st.latex(
        r"b_0 = 4(c+d)"
    )

    st.latex(
        rf"b_0 = 4({column_width:.3f}"
        rf"+{effective_depth:.3f})"
        rf" = {punching_perimeter:.3f}\ \mathrm{{m}}"
    )

    if punching_applicable:

        st.latex(
            r"V_p = q_u[B^2-(c+d)^2]"
        )

        st.latex(
            rf"V_p = {assumed_factored_pressure:.3f}"
            rf"\left[{provided_area:.3f}"
            rf"-({critical_side:.3f})^2\right]"
            rf" = {punching_force:.3f}"
            rf"\ \mathrm{{kN}}"
        )

    else:
        st.info(
            "The assumed punching control perimeter "
            "does not fit within the footing plan. "
            "This simplified punching expression "
            "is not evaluated."
        )

    # ======================================
    # 7. DEMAND SUMMARY
    # ======================================

    st.header("4. Structural Demand Summary")

    summary_df = pd.DataFrame({
        "Parameter": [
            "Average Service Pressure",
            "Assumed Factored Pressure",
            "Bending Moment Demand",
            "One-Way Shear Demand",
            "Punching Shear Demand"
        ],
        "Calculated Value": [
            f"{service_pressure:.3f} kN/m²",
            f"{assumed_factored_pressure:.3f} kN/m²",
            f"{bending_moment:.3f} kN·m/m",
            f"{one_way_shear:.3f} kN/m",
            (
                f"{punching_force:.3f} kN"
                if punching_force is not None
                else "Not evaluated"
            )
        ]
    })

    st.dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True
    )

    # ======================================
    # 8. ENGINEERING INTERPRETATION
    # ======================================

    st.header("5. Engineering Interpretation")

    st.write(
        f"The preliminary square footing dimension "
        f"is {adopted_side:.2f} m × {adopted_side:.2f} m."
    )

    st.write(
        f"The simplified average service bearing "
        f"pressure is {service_pressure:.3f} kN/m², "
        f"compared with the entered allowable value "
        f"of {sbc:.3f} kN/m²."
    )

    st.write(
        "Bending, one-way shear and punching shear "
        "values above are demands only. No structural "
        "strength capacities have been calculated, "
        "so the footing cannot be classified as "
        "structurally adequate."
    )

    # ======================================
    # 9. LIMITATIONS
    # ======================================

    st.header("6. Assumptions and Limitations")

    st.warning(
        "The analysis assumes a centrally loaded "
        "square footing and uniform soil pressure. "
        "It omits complete treatment of footing "
        "self-weight, soil overburden, load eccentricity, "
        "settlement, detailed reinforcement, structural "
        "capacity checks and independent code validation. "
        "This is not a verified IS 456 design and must "
        "not be used for construction."
    )

else:
    st.info(
        "Enter the input parameters and click "
        "'Calculate Preliminary Footing Analysis' "
        "to display the calculation report."
    )


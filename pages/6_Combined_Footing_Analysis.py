
import math
import pandas as pd
import streamlit as st

st.title("Combined Footing Analysis")

st.write(
    "Preliminary geometric and soil-pressure analysis "
    "of a rectangular combined footing supporting "
    "two columns."
)

st.caption(
    "Educational analysis module | "
    "Not a verified structural design"
)

st.divider()

# ==========================================
# 1. THEORY
# ==========================================

st.header("1. Introduction")

st.write(
    """
    A combined footing supports two or more columns
    on a common foundation.

    Combined footings may be considered where
    individual footings would overlap or where
    site boundary conditions restrict the
    placement of an isolated footing.

    This module considers two vertical column loads
    acting along the length of a rectangular footing.

    The preliminary geometry is selected so that
    the resultant of the entered column loads
    approximately coincides with the footing centroid.
    """
)

st.header("2. Analysis Assumptions")

st.markdown(
    """
    - Two columns carry vertical service loads.
    - Column loads act along the footing centreline.
    - A rectangular footing with uniform width is assumed.
    - Soil bearing pressure is treated as uniform when
      the resultant coincides with the footing centroid.
    - Footing self-weight and soil overburden are omitted.
    - Settlement and structural capacity are not checked.
    - Column positions are measured from the left edge.
    """
)

# ==========================================
# 3. INPUTS
# ==========================================

st.header("3. Input Parameters")

with st.form("combined_footing_form"):

    c1, c2 = st.columns(2)

    with c1:
        p1 = st.number_input(
            "Column 1 Service Load, P1 (kN)",
            min_value=1.0,
            value=800.0,
            step=50.0
        )

        p2 = st.number_input(
            "Column 2 Service Load, P2 (kN)",
            min_value=1.0,
            value=1200.0,
            step=50.0
        )

        spacing = st.number_input(
            "Column Centre-to-Centre Spacing, S (m)",
            min_value=0.1,
            value=3.0,
            step=0.1
        )

    with c2:
        sbc = st.number_input(
            "Allowable Soil Bearing Pressure (kN/m²)",
            min_value=1.0,
            value=200.0,
            step=10.0
        )

        left_distance = st.number_input(
            "Column 1 Centre from Left Edge, a (m)",
            min_value=0.05,
            value=0.5,
            step=0.05
        )

        column_width = st.number_input(
            "Assumed Column Width Along Length (m)",
            min_value=0.1,
            value=0.4,
            step=0.05
        )

    calculate = st.form_submit_button(
        "Calculate Combined Footing"
    )

if calculate:

    # ======================================
    # 4. LOAD AND RESULTANT
    # ======================================

    total_load = p1 + p2

    # Resultant measured from column 1 centre
    resultant_from_c1 = (
        p2 * spacing / total_load
    )

    # Resultant measured from left edge
    resultant_x = (
        left_distance + resultant_from_c1
    )

    # To align the footing centroid with resultant
    theoretical_length = 2 * resultant_x

    # Round length upward to 0.1 m
    adopted_length = (
        math.ceil(
            theoretical_length * 10 - 1e-10
        ) / 10
    )

    # Required area
    required_area = total_load / sbc

    # Required width based on adopted length
    required_width = (
        required_area / adopted_length
    )

    # Round width upward to 0.1 m
    adopted_width = (
        math.ceil(
            required_width * 10 - 1e-10
        ) / 10
    )

    # ======================================
    # 5. GEOMETRIC FEASIBILITY
    # ======================================

    column1_x = left_distance
    column2_x = left_distance + spacing

    left_clearance = (
        column1_x - column_width / 2
    )

    right_clearance = (
        adopted_length
        - column2_x
        - column_width / 2
    )

    if left_clearance < 0 or right_clearance < 0:
        st.error(
            "The calculated rectangular footing "
            "does not fully contain both columns "
            "along its length. Adjust the input "
            "geometry; this configuration is "
            "not feasible under the current "
            "centroid-alignment assumption."
        )

        st.write(
            f"Left column-edge clearance: "
            f"{left_clearance:.3f} m"
        )

        st.write(
            f"Right column-edge clearance: "
            f"{right_clearance:.3f} m"
        )

        st.stop()

    # ======================================
    # 6. SOIL PRESSURE
    # ======================================

    provided_area = (
        adopted_length * adopted_width
    )

    average_pressure = (
        total_load / provided_area
    )

    footing_centroid = (
        adopted_length / 2
    )

    eccentricity = (
        resultant_x - footing_centroid
    )

    # Simplified linear pressure distribution
    # for longitudinal eccentricity only.
    q_left = average_pressure * (
        1 - 6 * eccentricity / adopted_length
    )

    q_right = average_pressure * (
        1 + 6 * eccentricity / adopted_length
    )

    q_max = max(q_left, q_right)
    q_min = min(q_left, q_right)

    full_contact = q_min >= -1e-9

    # ======================================
    # 7. RESULT SUMMARY
    # ======================================

    st.header("4. Preliminary Geometry Results")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Adopted Footing Length",
        f"{adopted_length:.2f} m"
    )

    r2.metric(
        "Adopted Footing Width",
        f"{adopted_width:.2f} m"
    )

    r3.metric(
        "Provided Plan Area",
        f"{provided_area:.3f} m²"
    )

    geometry_df = pd.DataFrame({
        "Parameter": [
            "Total Column Load",
            "Required Footing Area",
            "Theoretical Length",
            "Adopted Length",
            "Adopted Width",
            "Column 1 Position",
            "Column 2 Position",
            "Resultant Position",
            "Footing Centroid",
            "Longitudinal Eccentricity"
        ],
        "Value": [
            f"{total_load:.2f} kN",
            f"{required_area:.3f} m²",
            f"{theoretical_length:.3f} m",
            f"{adopted_length:.2f} m",
            f"{adopted_width:.2f} m",
            f"{column1_x:.3f} m",
            f"{column2_x:.3f} m",
            f"{resultant_x:.3f} m",
            f"{footing_centroid:.3f} m",
            f"{eccentricity:.4f} m"
        ]
    })

    st.dataframe(
        geometry_df,
        hide_index=True,
        use_container_width=True
    )

    # ======================================
    # 8. FORMULAS
    # ======================================

    st.header("5. Engineering Formulas and Calculations")

    st.subheader("5.1 Total Service Load")

    st.latex(r"P = P_1 + P_2")

    st.latex(
        rf"P = {p1:.2f} + {p2:.2f}"
        rf" = {total_load:.2f}\ \mathrm{{kN}}"
    )

    st.subheader("5.2 Resultant Load Position")

    st.latex(
        r"x_R = a + \frac{P_2 S}{P_1 + P_2}"
    )

    st.latex(
        rf"x_R = {left_distance:.3f}"
        rf"+\frac{{{p2:.2f}\times{spacing:.3f}}}"
        rf"{{{total_load:.2f}}}"
        rf" = {resultant_x:.3f}\ \mathrm{{m}}"
    )

    st.write(
        "The resultant position is measured "
        "from the left edge of the footing."
    )

    st.subheader("5.3 Preliminary Footing Length")

    st.latex(r"L_{theoretical} = 2x_R")

    st.latex(
        rf"L_{{theoretical}} = "
        rf"2\times{resultant_x:.3f}"
        rf" = {theoretical_length:.3f}\ \mathrm{{m}}"
    )

    st.write(
        f"Adopted length rounded upward "
        f"to 0.1 m = {adopted_length:.2f} m."
    )

    st.subheader("5.4 Required Plan Area")

    st.latex(
        r"A_{req} = \frac{P}{q_{allow}}"
    )

    st.latex(
        rf"A_{{req}} = "
        rf"\frac{{{total_load:.2f}}}{{{sbc:.2f}}}"
        rf" = {required_area:.3f}\ \mathrm{{m^2}}"
    )

    st.subheader("5.5 Required Footing Width")

    st.latex(
        r"B_{required} = \frac{A_{req}}{L}"
    )

    st.latex(
        rf"B_{{required}} = "
        rf"\frac{{{required_area:.3f}}}"
        rf"{{{adopted_length:.2f}}}"
        rf" = {required_width:.3f}\ \mathrm{{m}}"
    )

    st.write(
        f"Adopted width rounded upward "
        f"to 0.1 m = {adopted_width:.2f} m."
    )

    st.subheader("5.6 Average Soil Bearing Pressure")

    st.latex(
        r"q_{avg} = \frac{P}{LB}"
    )

    st.latex(
        rf"q_{{avg}} = "
        rf"\frac{{{total_load:.2f}}}"
        rf"{{{adopted_length:.2f}"
        rf"\times{adopted_width:.2f}}}"
        rf" = {average_pressure:.3f}"
        rf"\ \mathrm{{kN/m^2}}"
    )

    st.subheader("5.7 Longitudinal Eccentricity")

    st.latex(
        r"e = x_R - \frac{L}{2}"
    )

    st.latex(
        rf"e = {resultant_x:.3f}"
        rf"-\frac{{{adopted_length:.2f}}}{{2}}"
        rf" = {eccentricity:.4f}\ \mathrm{{m}}"
    )

    st.subheader("5.8 Simplified Edge Bearing Pressures")

    st.latex(
        r"q_{left} = q_{avg}"
        r"\left(1-\frac{6e}{L}\right)"
    )

    st.latex(
        r"q_{right} = q_{avg}"
        r"\left(1+\frac{6e}{L}\right)"
    )

    st.latex(
        rf"q_{{left}} = {q_left:.3f}"
        rf"\ \mathrm{{kN/m^2}}"
    )

    st.latex(
        rf"q_{{right}} = {q_right:.3f}"
        rf"\ \mathrm{{kN/m^2}}"
    )

    st.write(
        "The linear edge-pressure expressions "
        "assume a rigid rectangular base and "
        "full soil contact. They consider "
        "longitudinal eccentricity only."
    )

    # ======================================
    # 9. BEARING PRESSURE SUMMARY
    # ======================================

    st.header("6. Soil Pressure Summary")

    pressure_df = pd.DataFrame({
        "Parameter": [
            "Average Applied Pressure",
            "Left Edge Pressure",
            "Right Edge Pressure",
            "Maximum Edge Pressure",
            "Minimum Edge Pressure",
            "Entered Allowable Pressure"
        ],
        "Value (kN/m²)": [
            average_pressure,
            q_left,
            q_right,
            q_max,
            q_min,
            sbc
        ]
    })

    st.dataframe(
        pressure_df.round(3),
        hide_index=True,
        use_container_width=True
    )

    if not full_contact:
        st.error(
            "The simplified full-contact assumption "
            "is not satisfied. The linear pressure "
            "results are not applicable as a "
            "complete contact-pressure solution."
        )

    elif q_max <= sbc + 1e-8:
        st.success(
            "Under the simplified full-contact "
            "pressure model, the maximum calculated "
            "edge pressure does not exceed the "
            "entered allowable value."
        )

    else:
        st.warning(
            "The maximum calculated edge pressure "
            "exceeds the entered allowable value."
        )

    # ======================================
    # 10. PRESSURE DISTRIBUTION
    # ======================================

    st.header("7. Longitudinal Pressure Distribution")

    chart_df = pd.DataFrame({
        "Distance from Left Edge (m)": [
            adopted_length * i / 20
            for i in range(21)
        ],
        "Pressure (kN/m²)": [
            q_left + (
                q_right - q_left
            ) * i / 20
            for i in range(21)
        ]
    })

    st.line_chart(
        chart_df.set_index(
            "Distance from Left Edge (m)"
        )
    )

    st.caption(
        "Illustrative linear pressure distribution "
        "based on the assumed rigid-base model."
    )

    # ======================================
    # 11. INTERPRETATION
    # ======================================

    st.header("8. Engineering Interpretation")

    st.write(
        f"The preliminary combined footing has "
        f"adopted dimensions of "
        f"{adopted_length:.2f} m × "
        f"{adopted_width:.2f} m."
    )

    st.write(
        f"The total service load is "
        f"{total_load:.2f} kN, with a resultant "
        f"located {resultant_x:.3f} m "
        f"from the left edge."
    )

    st.write(
        f"The longitudinal eccentricity is "
        f"{eccentricity:.4f} m."
    )

    st.write(
        "These calculations describe preliminary "
        "geometry and an idealized soil pressure "
        "distribution. They do not verify the "
        "structural adequacy of the footing."
    )

    # ======================================
    # 12. LIMITATIONS
    # ======================================

    st.header("9. Assumptions and Limitations")

    st.warning(
        "This model omits footing self-weight, "
        "overburden, column moments, lateral loads, "
        "biaxial eccentricity, soil-structure "
        "interaction, settlement, reinforcement "
        "design and structural capacity checks. "
        "The rectangular geometry may not be "
        "feasible for all input configurations. "
        "It is not a verified IS 456 design and "
        "must not be used for construction."
    )

else:
    st.info(
        "Enter the column loads and geometric "
        "parameters, then click "
        "'Calculate Combined Footing'."
    )

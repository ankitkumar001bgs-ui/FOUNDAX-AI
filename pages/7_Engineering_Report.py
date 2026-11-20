
import math
from io import BytesIO

import streamlit as st

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


# ==========================================
# FOUNDAX AI - PHASE 22
# ENGINEERING CALCULATION REPORT
# ==========================================

st.title("Engineering Calculation Report")

st.write(
    "Generate a detailed preliminary calculation "
    "report for a centrally loaded square isolated footing."
)

st.caption(
    "Educational engineering report | "
    "Not a certified structural design"
)

st.divider()


# ==========================================
# 1. INPUT PARAMETERS
# ==========================================

st.header("1. Report Input Parameters")

with st.form("engineering_report_form"):

    c1, c2 = st.columns(2)

    with c1:
        project_name = st.text_input(
            "Project Name",
            value="FOUNDAX AI - Isolated Footing Study"
        )

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
            "Illustrative Load Multiplier",
            min_value=1.0,
            value=1.5,
            step=0.1
        )

    generate = st.form_submit_button(
        "Generate Calculation Report"
    )


# ==========================================
# 2. CALCULATION FUNCTION
# ==========================================

def calculate_results(
    load,
    sbc,
    column_width,
    overall_depth,
    effective_depth,
    load_factor
):

    if effective_depth >= overall_depth:
        raise ValueError(
            "Effective depth must be smaller "
            "than overall depth."
        )

    required_area = load / sbc

    theoretical_side = math.sqrt(required_area)

    adopted_side = (
        math.ceil(theoretical_side * 10 - 1e-10) / 10
    )

    if column_width >= adopted_side:
        raise ValueError(
            "Column width must be smaller "
            "than the adopted footing side."
        )

    provided_area = adopted_side ** 2

    service_pressure = load / provided_area

    factored_pressure = (
        load_factor * load / provided_area
    )

    projection = (
        adopted_side - column_width
    ) / 2

    bending_moment = (
        factored_pressure * projection ** 2 / 2
    )

    shear_length = max(
        projection - effective_depth,
        0
    )

    one_way_shear = (
        factored_pressure * shear_length
    )

    critical_side = (
        column_width + effective_depth
    )

    punching_perimeter = (
        4 * critical_side
    )

    punching_force = None

    if critical_side < adopted_side:
        punching_force = (
            factored_pressure
            * (provided_area - critical_side ** 2)
        )

    return {
        "required_area": required_area,
        "theoretical_side": theoretical_side,
        "adopted_side": adopted_side,
        "provided_area": provided_area,
        "service_pressure": service_pressure,
        "factored_pressure": factored_pressure,
        "projection": projection,
        "bending_moment": bending_moment,
        "shear_length": shear_length,
        "one_way_shear": one_way_shear,
        "critical_side": critical_side,
        "punching_perimeter": punching_perimeter,
        "punching_force": punching_force,
    }


# ==========================================
# 3. PDF GENERATION FUNCTION
# ==========================================

def build_pdf(project_name, inputs, results):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=(595.28, 841.89),
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    styles["Title"].alignment = TA_CENTER
    styles["Title"].fontSize = 17
    styles["Title"].leading = 22

    styles["Heading2"].spaceBefore = 15
    styles["Heading2"].spaceAfter = 8

    styles["BodyText"].leading = 15

    story = []

    def add_text(text, style="BodyText"):
        story.append(
            Paragraph(text, styles[style])
        )
        story.append(Spacer(1, 7))

    def add_heading(text):
        add_text(text, "Heading2")

    def add_table(rows):
        formatted = [
            [
                Paragraph(str(cell), styles["BodyText"])
                for cell in row
            ]
            for row in rows
        ]

        table = Table(
            formatted,
            colWidths=[250, 245],
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E8EDF3")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        story.append(table)
        story.append(Spacer(1, 12))

    # ---------- TITLE ----------

    add_text(
        "FOUNDAX AI",
        "Title"
    )

    add_text(
        "PRELIMINARY ISOLATED FOOTING "
        "CALCULATION REPORT",
        "Heading2"
    )

    add_text(
        f"<b>Project:</b> {project_name}"
    )

    add_text(
        "<b>Report Type:</b> Educational "
        "Preliminary Engineering Calculation"
    )

    # ---------- INTRODUCTION ----------

    add_heading("1. Introduction")

    add_text(
        "This report documents preliminary "
        "area sizing, assumed bearing pressure, "
        "and simplified structural demand calculations "
        "for a centrally loaded square isolated footing."
    )

    # ---------- INPUT TABLE ----------

    add_heading("2. Input Parameters")

    add_table([
        ["Parameter", "Input Value"],
        [
            "Column Service Load",
            f"{inputs['load']:.2f} kN"
        ],
        [
            "Allowable Bearing Pressure",
            f"{inputs['sbc']:.2f} kN/m2"
        ],
        [
            "Square Column Width",
            f"{inputs['column_width']:.3f} m"
        ],
        [
            "Assumed Overall Depth",
            f"{inputs['overall_depth']:.3f} m"
        ],
        [
            "Assumed Effective Depth",
            f"{inputs['effective_depth']:.3f} m"
        ],
        [
            "Illustrative Load Multiplier",
            f"{inputs['load_factor']:.2f}"
        ],
    ])

    # ---------- FORMULAS ----------

    add_heading("3. Engineering Calculations")

    add_text(
        "<b>3.1 Required Plan Area</b>"
    )

    add_text(
        "Formula: A_required = P / q_allow"
    )

    add_text(
        f"Substitution: "
        f"{inputs['load']:.2f} / "
        f"{inputs['sbc']:.2f}"
        f" = {results['required_area']:.3f} m2"
    )

    add_text(
        "<b>3.2 Square Footing Side</b>"
    )

    add_text(
        "Formula: B = sqrt(A_required)"
    )

    add_text(
        f"Theoretical side = "
        f"{results['theoretical_side']:.3f} m"
    )

    add_text(
        f"Adopted side, rounded upward to 0.1 m "
        f"= {results['adopted_side']:.2f} m"
    )

    add_text(
        "<b>3.3 Provided Plan Area</b>"
    )

    add_text(
        "Formula: A_provided = B x B"
    )

    add_text(
        f"{results['adopted_side']:.2f} x "
        f"{results['adopted_side']:.2f}"
        f" = {results['provided_area']:.3f} m2"
    )

    add_text(
        "<b>3.4 Average Service Bearing Pressure</b>"
    )

    add_text(
        "Formula: q_service = P / A_provided"
    )

    add_text(
        f"{inputs['load']:.2f} / "
        f"{results['provided_area']:.3f}"
        f" = {results['service_pressure']:.3f} kN/m2"
    )

    add_text(
        "<b>3.5 Assumed Factored Pressure</b>"
    )

    add_text(
        "Formula: q_u = gamma x P / A_provided"
    )

    add_text(
        f"({inputs['load_factor']:.2f} x "
        f"{inputs['load']:.2f}) / "
        f"{results['provided_area']:.3f}"
        f" = {results['factored_pressure']:.3f} kN/m2"
    )

    add_text(
        "<b>3.6 Column-to-Edge Projection</b>"
    )

    add_text(
        "Formula: a = (B - c) / 2"
    )

    add_text(
        f"({results['adopted_side']:.3f} - "
        f"{inputs['column_width']:.3f}) / 2"
        f" = {results['projection']:.3f} m"
    )

    add_text(
        "<b>3.7 Simplified Bending Moment Demand</b>"
    )

    add_text(
        "Formula: M_u = q_u x a^2 / 2"
    )

    add_text(
        f"{results['factored_pressure']:.3f} x "
        f"({results['projection']:.3f})^2 / 2"
        f" = {results['bending_moment']:.3f} kN.m/m"
    )

    add_text(
        "<b>3.8 Simplified One-Way Shear Demand</b>"
    )

    add_text(
        "Formula: V_u = q_u x max(a - d, 0)"
    )

    add_text(
        f"{results['factored_pressure']:.3f} x "
        f"{results['shear_length']:.3f}"
        f" = {results['one_way_shear']:.3f} kN/m"
    )

    add_text(
        "<b>3.9 Simplified Punching Shear Demand</b>"
    )

    add_text(
        "Assumed control perimeter: "
        "b0 = 4 x (c + d)"
    )

    add_text(
        f"b0 = {results['punching_perimeter']:.3f} m"
    )

    if results["punching_force"] is not None:
        add_text(
            "Formula: V_p = q_u x "
            "[B^2 - (c + d)^2]"
        )

        add_text(
            f"V_p = "
            f"{results['factored_pressure']:.3f} x "
            f"[{results['provided_area']:.3f} - "
            f"({results['critical_side']:.3f})^2]"
            f" = {results['punching_force']:.3f} kN"
        )
    else:
        add_text(
            "Punching demand not evaluated: "
            "the assumed control perimeter "
            "does not fit inside the footing."
        )

    # ---------- SUMMARY ----------

    add_heading("4. Calculation Summary")

    punching_text = (
        f"{results['punching_force']:.3f} kN"
        if results["punching_force"] is not None
        else "Not evaluated"
    )

    add_table([
        ["Parameter", "Calculated Value"],
        [
            "Adopted Footing Size",
            f"{results['adopted_side']:.2f} m x "
            f"{results['adopted_side']:.2f} m"
        ],
        [
            "Provided Area",
            f"{results['provided_area']:.3f} m2"
        ],
        [
            "Service Bearing Pressure",
            f"{results['service_pressure']:.3f} kN/m2"
        ],
        [
            "Assumed Factored Pressure",
            f"{results['factored_pressure']:.3f} kN/m2"
        ],
        [
            "Bending Moment Demand",
            f"{results['bending_moment']:.3f} kN.m/m"
        ],
        [
            "One-Way Shear Demand",
            f"{results['one_way_shear']:.3f} kN/m"
        ],
        [
            "Punching Shear Demand",
            punching_text
        ],
    ])

    # ---------- INTERPRETATION ----------

    add_heading("5. Engineering Interpretation")

    add_text(
        "The adopted footing area meets the simplified "
        "plan-area requirement based on the entered "
        "service load and allowable bearing pressure."
    )

    add_text(
        "The bending and shear values are calculated "
        "demands only. Structural capacities have "
        "not been checked."
    )

    # ---------- LIMITATIONS ----------

    add_heading("6. Assumptions and Limitations")

    add_text(
        "The calculations assume a centrally loaded "
        "square footing with uniform soil pressure. "
        "They omit complete consideration of footing "
        "self-weight, soil overburden, eccentric loads, "
        "settlement, reinforcement design, and "
        "structural capacity verification."
    )

    add_text(
        "The load multiplier is illustrative and "
        "does not represent a verified design "
        "load combination."
    )

    add_text(
        "<b>Conclusion:</b> This document is an "
        "educational preliminary calculation report. "
        "It does not establish IS 456 compliance "
        "or construction safety. Independent "
        "engineering verification is required."
    )

    document.build(story)

    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


# ==========================================
# 4. GENERATE REPORT
# ==========================================

if generate:

    try:
        results = calculate_results(
            load,
            sbc,
            column_width,
            overall_depth,
            effective_depth,
            load_factor
        )

        inputs = {
            "load": load,
            "sbc": sbc,
            "column_width": column_width,
            "overall_depth": overall_depth,
            "effective_depth": effective_depth,
            "load_factor": load_factor
        }

        pdf_bytes = build_pdf(
            project_name,
            inputs,
            results
        )

        st.success(
            "Preliminary calculation report generated."
        )

        st.header("2. Report Summary")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Footing Side",
            f"{results['adopted_side']:.2f} m"
        )

        c2.metric(
            "Provided Area",
            f"{results['provided_area']:.3f} m²"
        )

        c3.metric(
            "Service Bearing Pressure",
            f"{results['service_pressure']:.3f} kN/m²"
        )

        st.subheader("Download PDF Report")

        st.download_button(
            label="Download Engineering Calculation Report",
            data=pdf_bytes,
            file_name="FOOTOPT_AI_Isolated_Footing_Report.pdf",
            mime="application/pdf"
        )

        st.info(
            "The downloaded PDF includes input values, "
            "formulas, numerical substitutions, "
            "results and engineering limitations."
        )

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            f"Report generation failed: {error}"
        )

else:
    st.info(
        "Enter the input parameters and click "
        "'Generate Calculation Report'."
    )


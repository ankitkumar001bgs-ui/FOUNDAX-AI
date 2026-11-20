
import math

import pandas as pd
import streamlit as st
from scipy.optimize import differential_evolution

st.title("Footing Cost Optimization")
st.subheader("Differential Evolution Algorithm")

st.write(
    "This module compares preliminary square footing "
    "configurations using an illustrative construction "
    "cost model."
)

st.caption(
    "Educational optimization model | "
    "Structural safety is not verified"
)

st.divider()

# ==========================================
# 1. METHODOLOGY
# ==========================================

st.header("1. Optimization Methodology")

st.write(
    """
    Differential Evolution is a population-based
    numerical optimization algorithm.

    It searches for combinations of design variables
    that minimize a specified objective function
    within defined search bounds.

    In this prototype, the decision variables are
    the square footing side length and assumed
    footing thickness.

    The objective is to minimize estimated concrete,
    assumed reinforcement and excavation costs.
    """
)

st.subheader("1.1 Decision Variables")

st.latex(r"x = [B, D]")

st.write(
    "B = Square footing side length (m)"
)

st.write(
    "D = Assumed overall footing thickness (m)"
)

st.subheader("1.2 Objective Function")

st.latex(
    r"C_{total} = C_c + C_s + C_e"
)

st.latex(
    r"C_c = B^2 D R_c"
)

st.latex(
    r"C_s = B^2 D \rho_s R_s"
)

st.latex(
    r"C_e = B^2 H_e R_e"
)

st.write(
    """
    Where:

    - C_total = Total estimated cost (Rs)
    - C_c = Concrete cost (Rs)
    - C_s = Assumed reinforcement cost (Rs)
    - C_e = Excavation cost (Rs)
    - B = Footing side length (m)
    - D = Assumed footing thickness (m)
    - H_e = Excavation depth (m)
    - R_c = Concrete unit rate (Rs/m³)
    - R_s = Steel unit rate (Rs/kg)
    - R_e = Excavation unit rate (Rs/m³)
    - rho_s = Assumed reinforcement quantity (kg/m³)
    """
)

st.subheader("1.3 Preliminary Area Requirement")

st.latex(
    r"B^2 \geq \frac{P}{q_{allow}}"
)

st.write(
    "The lower search bound for B is calculated "
    "from the preliminary required plan area."
)

st.warning(
    "The optimization does not include verified "
    "bending, shear, punching shear, settlement "
    "or reinforcement design constraints. "
    "Therefore, the minimum-cost result is not "
    "a structurally optimized footing."
)

# ==========================================
# 2. INPUT PARAMETERS
# ==========================================

st.header("2. Input Parameters")

with st.form("professional_cost_form"):

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

        concrete_rate = st.number_input(
            "Concrete Rate (Rs/m³)",
            min_value=0.0,
            value=7000.0,
            step=100.0
        )

        steel_rate = st.number_input(
            "Steel Rate (Rs/kg)",
            min_value=0.0,
            value=65.0,
            step=1.0
        )

    with c2:
        steel_factor = st.number_input(
            "Assumed Steel Quantity (kg/m³)",
            min_value=0.0,
            value=80.0,
            step=5.0
        )

        excavation_rate = st.number_input(
            "Excavation Rate (Rs/m³)",
            min_value=0.0,
            value=300.0,
            step=25.0
        )

        excavation_depth = st.number_input(
            "Excavation Depth, H_e (m)",
            min_value=0.1,
            value=1.5,
            step=0.1
        )

        baseline_thickness = st.number_input(
            "Baseline Assumed Thickness (m)",
            min_value=0.4,
            max_value=0.8,
            value=0.6,
            step=0.05
        )

    optimize = st.form_submit_button(
        "Run Cost Optimization"
    )

# ==========================================
# 3. CALCULATION FUNCTIONS
# ==========================================

def calculate_cost(side, thickness, rates):
    area = side ** 2

    concrete_volume = area * thickness

    assumed_steel_weight = (
        concrete_volume * rates["steel_factor"]
    )

    excavation_volume = (
        area * rates["excavation_depth"]
    )

    concrete_cost = (
        concrete_volume * rates["concrete_rate"]
    )

    steel_cost = (
        assumed_steel_weight * rates["steel_rate"]
    )

    excavation_cost = (
        excavation_volume * rates["excavation_rate"]
    )

    total_cost = (
        concrete_cost + steel_cost + excavation_cost
    )

    return {
        "side": side,
        "thickness": thickness,
        "area": area,
        "concrete_volume": concrete_volume,
        "steel_weight": assumed_steel_weight,
        "excavation_volume": excavation_volume,
        "concrete_cost": concrete_cost,
        "steel_cost": steel_cost,
        "excavation_cost": excavation_cost,
        "total_cost": total_cost
    }


# ==========================================
# 4. OPTIMIZATION RESULTS
# ==========================================

if optimize:

    rates = {
        "concrete_rate": concrete_rate,
        "steel_rate": steel_rate,
        "steel_factor": steel_factor,
        "excavation_rate": excavation_rate,
        "excavation_depth": excavation_depth
    }

    required_area = load / sbc
    theoretical_side = math.sqrt(required_area)

    # Baseline: round side upward to 0.1 m,
    # then add an illustrative 0.3 m margin.
    baseline_side = (
        math.ceil(
            theoretical_side * 10 - 1e-10
        ) / 10
    ) + 0.3

    baseline = calculate_cost(
        baseline_side,
        baseline_thickness,
        rates
    )

    def objective(x):
        side, thickness = x

        return calculate_cost(
            side,
            thickness,
            rates
        )["total_cost"]

    bounds = [
        (theoretical_side, theoretical_side + 1.0),
        (0.4, 0.8)
    ]

    result = differential_evolution(
        objective,
        bounds=bounds,
        seed=42,
        maxiter=100,
        polish=True
    )

    optimized_side, optimized_thickness = result.x

    optimized = calculate_cost(
        optimized_side,
        optimized_thickness,
        rates
    )

    if (
        not result.success
        or optimized["area"] + 1e-8 < required_area
    ):
        st.error(
            "The optimizer did not return a valid "
            "preliminary area-constrained result."
        )
        st.stop()

    savings = (
        baseline["total_cost"]
        - optimized["total_cost"]
    )

    savings_percentage = (
        savings / baseline["total_cost"] * 100
        if baseline["total_cost"] > 0
        else 0
    )

    st.header("3. Optimization Results")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Optimized Footing Side",
        f"{optimized_side:.3f} m"
    )

    r2.metric(
        "Assumed Thickness",
        f"{optimized_thickness:.3f} m"
    )

    r3.metric(
        "Estimated Minimum Cost",
        f"Rs {optimized['total_cost']:,.2f}"
    )

    st.subheader("3.1 Preliminary Area Verification")

    st.latex(
        rf"A_{{req}} = "
        rf"\frac{{{load:.2f}}}{{{sbc:.2f}}}"
        rf" = {required_area:.3f}\ \mathrm{{m^2}}"
    )

    st.latex(
        rf"A_{{provided}} = "
        rf"({optimized_side:.3f})^2"
        rf" \approx {optimized['area']:.3f}"
        rf"\ \mathrm{{m^2}}"
    )

    st.write(
        "The optimized continuous side length "
        "satisfies the simplified area requirement."
    )

    st.info(
        "The optimized dimensions are continuous "
        "numerical values. Practical construction "
        "dimensions would need appropriate rounding "
        "and complete engineering verification."
    )

    # ======================================
    # 5. QUANTITY CALCULATIONS
    # ======================================

    st.header("4. Material Quantity Calculations")

    st.subheader("4.1 Concrete Volume")

    st.latex(
        r"V_c = B^2 D"
    )

    st.latex(
        rf"V_c = "
        rf"({optimized_side:.3f})^2"
        rf"\times {optimized_thickness:.3f}"
        rf"\approx {optimized['concrete_volume']:.3f}"
        rf"\ \mathrm{{m^3}}"
    )

    st.subheader("4.2 Assumed Steel Quantity")

    st.latex(
        r"W_s = V_c \rho_s"
    )

    st.latex(
        rf"W_s = "
        rf"{optimized['concrete_volume']:.3f}"
        rf"\times {steel_factor:.2f}"
        rf"\approx {optimized['steel_weight']:.2f}"
        rf"\ \mathrm{{kg}}"
    )

    st.write(
        "Steel quantity is based on an assumed "
        "kg/m³ factor, not reinforcement design."
    )

    st.subheader("4.3 Excavation Volume")

    st.latex(
        r"V_e = B^2 H_e"
    )

    st.latex(
        rf"V_e = "
        rf"({optimized_side:.3f})^2"
        rf"\times {excavation_depth:.2f}"
        rf"\approx {optimized['excavation_volume']:.3f}"
        rf"\ \mathrm{{m^3}}"
    )

    # ======================================
    # 6. COST BREAKDOWN
    # ======================================

    st.header("5. Estimated Cost Breakdown")

    cost_df = pd.DataFrame({
        "Cost Component": [
            "Concrete",
            "Assumed Reinforcement",
            "Excavation",
            "Total"
        ],
        "Estimated Cost (Rs)": [
            optimized["concrete_cost"],
            optimized["steel_cost"],
            optimized["excavation_cost"],
            optimized["total_cost"]
        ]
    })

    st.dataframe(
        cost_df.round(2),
        hide_index=True,
        use_container_width=True
    )

    st.bar_chart(
        cost_df.iloc[:3].set_index("Cost Component")
    )

    # ======================================
    # 7. BASELINE COMPARISON
    # ======================================

    st.header("6. Baseline vs Optimized Comparison")

    st.write(
        "The baseline is an illustrative comparison "
        "case, not an independently designed footing."
    )

    comparison_df = pd.DataFrame({
        "Parameter": [
            "Footing Side (m)",
            "Assumed Thickness (m)",
            "Plan Area (m²)",
            "Concrete Volume (m³)",
            "Assumed Steel (kg)",
            "Excavation Volume (m³)",
            "Estimated Total Cost (Rs)"
        ],
        "Baseline": [
            baseline["side"],
            baseline["thickness"],
            baseline["area"],
            baseline["concrete_volume"],
            baseline["steel_weight"],
            baseline["excavation_volume"],
            baseline["total_cost"]
        ],
        "Optimized": [
            optimized["side"],
            optimized["thickness"],
            optimized["area"],
            optimized["concrete_volume"],
            optimized["steel_weight"],
            optimized["excavation_volume"],
            optimized["total_cost"]
        ]
    })

    st.dataframe(
        comparison_df.round(3),
        hide_index=True,
        use_container_width=True
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Estimated Cost Difference",
        f"Rs {savings:,.2f}"
    )

    c2.metric(
        "Difference Relative to Baseline",
        f"{savings_percentage:.2f}%"
    )

    # ======================================
    # 8. ENGINEERING INTERPRETATION
    # ======================================

    st.header("7. Engineering Interpretation")

    st.write(
        "The optimizer searches within the defined "
        "side-length and thickness bounds to minimize "
        "the illustrative construction cost function."
    )

    st.write(
        "Because the current cost function increases "
        "with both footing size and thickness when "
        "unit rates are positive, the optimizer "
        "normally selects values near the lower bounds."
    )

    st.write(
        "Any estimated cost reduction is relative "
        "to the chosen illustrative baseline only. "
        "It does not demonstrate a reduction compared "
        "with a code-compliant engineering design."
    )

    st.header("8. Limitations")

    st.warning(
        "The model excludes structural strength "
        "capacity checks, reinforcement detailing, "
        "settlement, load eccentricity, footing "
        "self-weight and other design requirements. "
        "The assumed steel factor is not a calculated "
        "reinforcement quantity. The output is not "
        "verified for IS 456 compliance and must "
        "not be used for construction."
    )

else:
    st.info(
        "Enter the cost parameters and click "
        "'Run Cost Optimization' to generate "
        "the detailed calculation report."
    )



import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================
# FOOTOPT AI - PHASE 20
# VALIDATION AND TESTING DASHBOARD
# ==========================================

st.set_page_config(
    page_title="FOOTOPT AI | Validation",
    layout="wide"
)

PROJECT_DIR = Path(__file__).resolve().parent.parent

METRICS_PATH = (
    PROJECT_DIR
    / "machine_learning"
    / "model_metrics_v2.json"
)

TEST_RESULTS_PATH = (
    PROJECT_DIR
    / "machine_learning"
    / "test_predictions_v2.csv"
)

TEST_SCRIPT = PROJECT_DIR / "test_footing.py"

st.title("Validation and Testing")

st.write(
    "This page documents the numerical testing, "
    "machine learning evaluation and current "
    "engineering validation status of FOOTOPT AI."
)

st.caption(
    "Educational research prototype | "
    "Validation evidence and limitations"
)

st.divider()

# ==========================================
# 1. VALIDATION FRAMEWORK
# ==========================================

st.header("1. Validation Framework")

st.write(
    "Validation is organized into three levels:"
)

validation_levels = pd.DataFrame({
    "Level": [
        "Level 1",
        "Level 2",
        "Level 3"
    ],
    "Validation Type": [
        "Arithmetic and Software Testing",
        "Machine Learning Evaluation",
        "Engineering Design Verification"
    ],
    "Purpose": [
        "Check numerical consistency and input handling",
        "Evaluate predictions on held-out synthetic data",
        "Compare with independent engineering references"
    ],
    "Current Status": [
        "Implemented for selected calculations",
        "Implemented for Random Forest v2",
        "Not yet completed"
    ]
})

st.dataframe(
    validation_levels,
    hide_index=True,
    use_container_width=True
)

# ==========================================
# 2. AUTOMATED SOFTWARE TESTING
# ==========================================

st.header("2. Automated Software Testing")

st.write(
    "The automated test suite checks selected "
    "preliminary calculation functions using "
    "Python's unittest framework."
)

st.subheader("2.1 Run Automated Tests")

if not TEST_SCRIPT.exists():
    st.warning(
        "test_footing.py was not found in "
        "the main project folder."
    )
else:
    st.write(
        "Test file: test_footing.py"
    )

    if st.button(
        "Run Automated Test Suite",
        key="run_validation_tests"
    ):
        with st.spinner("Running tests..."):

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(TEST_SCRIPT)
                    ],
                    cwd=str(PROJECT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                output = (
                    result.stdout
                    + "\n"
                    + result.stderr
                )

                if result.returncode == 0:
                    st.success(
                        "Automated test suite passed."
                    )
                else:
                    st.error(
                        "One or more automated tests failed."
                    )

                st.code(
                    output.strip(),
                    language="text"
                )

            except subprocess.TimeoutExpired:
                st.error(
                    "The test suite exceeded "
                    "the 30-second time limit."
                )

            except Exception as error:
                st.error(
                    f"Unable to run tests: {error}"
                )

st.subheader("2.2 Scope of Current Tests")

st.write(
    "The current tests cover selected cases involving "
    "preliminary area sizing, bending demand, "
    "one-way shear demand, punching shear demand "
    "and invalid inputs."
)

st.info(
    "Passing these tests confirms that the "
    "implemented functions satisfy their "
    "specified arithmetic checks. "
    "It does not independently prove that "
    "the engineering formulas are complete "
    "or code compliant."
)

# ==========================================
# 3. ANALYTICAL REFERENCE CASE
# ==========================================

st.header("3. Analytical Reference Calculation")

st.write(
    "This example demonstrates the simplified "
    "preliminary footing area calculation."
)

reference_load = 1000.0
reference_sbc = 200.0

reference_area = reference_load / reference_sbc
reference_side = math.ceil(
    math.sqrt(reference_area) * 10 - 1e-10
) / 10

reference_provided_area = reference_side ** 2
reference_pressure = (
    reference_load / reference_provided_area
)

st.subheader("3.1 Input Values")

reference_inputs = pd.DataFrame({
    "Parameter": [
        "Column Service Load",
        "Allowable Soil Bearing Pressure"
    ],
    "Value": [
        "1000 kN",
        "200 kN/m²"
    ]
})

st.dataframe(
    reference_inputs,
    hide_index=True,
    use_container_width=True
)

st.subheader("3.2 Formula and Substitution")

st.latex(
    r"A_{req} = \frac{P}{q_{allow}}"
)

st.latex(
    r"A_{req} = \frac{1000}{200}"
    r" = 5.000\ \mathrm{m^2}"
)

st.latex(
    r"B = \sqrt{5.000}"
    r" = 2.236\ \mathrm{m}"
)

st.write(
    "Adopted square footing side, rounded "
    "upward to 0.1 m = 2.30 m."
)

st.latex(
    r"A_{provided} = 2.30^2"
    r" = 5.290\ \mathrm{m^2}"
)

st.latex(
    r"q_s = \frac{1000}{5.290}"
    r" = 189.036\ \mathrm{kN/m^2}"
)

st.subheader("3.3 Reference Results")

reference_results = pd.DataFrame({
    "Parameter": [
        "Required Area",
        "Adopted Side",
        "Provided Area",
        "Average Service Pressure"
    ],
    "Calculated Value": [
        f"{reference_area:.3f} m²",
        f"{reference_side:.2f} m",
        f"{reference_provided_area:.3f} m²",
        f"{reference_pressure:.3f} kN/m²"
    ]
})

st.dataframe(
    reference_results,
    hide_index=True,
    use_container_width=True
)

st.write(
    "This reference case verifies arithmetic "
    "for the stated simplified area-sizing "
    "assumptions. It is not an independent "
    "structural design benchmark."
)

# ==========================================
# 4. MACHINE LEARNING TEST METRICS
# ==========================================

st.header("4. Machine Learning Test Evaluation")

if METRICS_PATH.exists():

    try:
        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            metrics = json.load(file)

        st.write(
            "Random Forest v2 was evaluated using "
            "a reproducible training and testing "
            "split of the synthetic dataset."
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Held-Out Test MAE",
            f"{metrics['test_mae_m']:.4f} m"
        )

        m2.metric(
            "Held-Out Test RMSE",
            f"{metrics['test_rmse_m']:.4f} m"
        )

        m3.metric(
            "Held-Out Test R²",
            f"{metrics['test_r2']:.4f}"
        )

        st.subheader("4.1 Model Configuration")

        model_details = pd.DataFrame({
            "Parameter": [
                "Algorithm",
                "Dataset Type",
                "Total Records",
                "Training Records",
                "Testing Records",
                "Number of Trees",
                "Random State"
            ],
            "Value": [
                metrics["algorithm"],
                metrics["dataset_type"],
                metrics["total_records"],
                metrics["training_records"],
                metrics["testing_records"],
                metrics["n_estimators"],
                metrics["random_state"]
            ]
        })

        st.dataframe(
            model_details,
            hide_index=True,
            use_container_width=True
        )

        st.subheader("4.2 Evaluation Formulas")

        st.latex(
            r"MAE = \frac{1}{n}"
            r"\sum_{i=1}^{n}|y_i-\hat{y}_i|"
        )

        st.latex(
            r"RMSE = \sqrt{\frac{1}{n}"
            r"\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}"
        )

        st.latex(
            r"R^2 = 1 - "
            r"\frac{\sum_i(y_i-\hat{y}_i)^2}"
            r"{\sum_i(y_i-\bar{y})^2}"
        )

        st.write(
            "MAE and RMSE are measured in metres. "
            "R² is dimensionless."
        )

    except Exception as error:
        st.error(
            f"Unable to read ML metrics: {error}"
        )

else:
    st.warning(
        "Model evaluation file not found. "
        "Run train_model_v2.py first."
    )

# ==========================================
# 5. TEST PREDICTIONS
# ==========================================

st.header("5. Held-Out Prediction Analysis")

if TEST_RESULTS_PATH.exists():

    try:
        test_df = pd.read_csv(
            TEST_RESULTS_PATH
        )

        required_columns = [
            "actual_side_m",
            "predicted_side_m",
            "absolute_error_m"
        ]

        if all(
            col in test_df.columns
            for col in required_columns
        ):

            st.subheader("5.1 Test Prediction Table")

            st.dataframe(
                test_df.head(25).round(4),
                hide_index=True,
                use_container_width=True
            )

            st.subheader("5.2 Actual vs Predicted")

            chart_df = test_df[
                [
                    "actual_side_m",
                    "predicted_side_m"
                ]
            ].head(100)

            st.line_chart(
                chart_df.reset_index(drop=True)
            )

            st.subheader("5.3 Error Distribution")

            st.bar_chart(
                test_df[
                    ["absolute_error_m"]
                ].head(50).reset_index(drop=True)
            )

            st.write(
                "These plots illustrate prediction "
                "differences for selected held-out "
                "synthetic test records."
            )

        else:
            st.warning(
                "Test predictions file does not "
                "contain the expected columns."
            )

    except Exception as error:
        st.error(
            f"Unable to read test predictions: {error}"
        )

else:
    st.warning(
        "Test prediction file not found. "
        "Run train_model_v2.py first."
    )

# ==========================================
# 6. ENGINEERING VALIDATION STATUS
# ==========================================

st.header("6. Engineering Validation Status")

status_df = pd.DataFrame({
    "Verification Item": [
        "Preliminary Area Calculation",
        "Software Arithmetic Tests",
        "Random Forest Held-Out Evaluation",
        "Bending Capacity Verification",
        "One-Way Shear Capacity Verification",
        "Punching Shear Capacity Verification",
        "Reinforcement Detailing",
        "Settlement Verification",
        "Independent Engineering Benchmarks",
        "Complete IS 456 Compliance"
    ],
    "Status": [
        "Simplified arithmetic implemented",
        "Selected tests implemented",
        "Implemented on synthetic data",
        "Not completed",
        "Not completed",
        "Not completed",
        "Not completed",
        "Not completed",
        "Not completed",
        "Not established"
    ]
})

st.dataframe(
    status_df,
    hide_index=True,
    use_container_width=True
)

st.subheader("6.1 Interpretation")

st.write(
    "The current validation evidence supports "
    "software arithmetic consistency and "
    "machine learning performance on synthetic "
    "held-out records."
)

st.write(
    "It does not establish complete structural "
    "design validity, geotechnical adequacy "
    "or compliance with engineering codes."
)

# ==========================================
# 7. FUTURE VALIDATION PLAN
# ==========================================

st.header("7. Future Validation Plan")

st.markdown(
    """
    1. Collect independently verified footing
       calculation examples.

    2. Compare computed bending and shear demands
       against documented reference calculations.

    3. Implement and verify structural capacity
       checks using appropriate design references.

    4. Introduce reinforcement detailing checks.

    5. Evaluate settlement and other geotechnical
       considerations.

    6. Expand the automated test suite to cover
       boundary cases and regression testing.

    7. Document all assumptions, units, source
       references and calculation limitations.
    """
)

st.header("8. Overall Validation Conclusion")

st.warning(
    "FOOTOPT AI is a functioning educational "
    "research prototype. Its arithmetic testing "
    "and synthetic-data ML evaluation are "
    "implemented, but independent engineering "
    "verification remains incomplete. "
    "The results must not be used for actual "
    "construction without qualified engineering "
    "review."
)

st.divider()

st.caption(
    "FOUNDAX AI | Validation and Testing Module"
)


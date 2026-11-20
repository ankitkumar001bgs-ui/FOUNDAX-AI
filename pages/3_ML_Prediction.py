
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ==========================================
# FOOTOPT AI - PHASE 17
# MACHINE LEARNING PREDICTION AND EVALUATION
# ==========================================

st.title("Machine Learning-Based Footing Prediction")

st.write(
    "Random Forest regression for preliminary "
    "square isolated footing dimension prediction."
)

st.caption(
    "Educational ML prototype | "
    "Predictions are not verified structural designs"
)

st.divider()

# ------------------------------------------
# 1. FILE PATHS
# ------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_DIR
    / "machine_learning"
    / "isolated_footing_model_v2.pkl"
)

DATASET_PATH = (
    PROJECT_DIR
    / "dataset"
    / "isolated_footing_dataset.csv"
)

if not MODEL_PATH.exists():
    st.error(
        "Trained model file not found: "
        f"{MODEL_PATH}"
    )
    st.stop()

if not DATASET_PATH.exists():
    st.error(
        "Dataset file not found: "
        f"{DATASET_PATH}"
    )
    st.stop()

# ------------------------------------------
# 2. LOAD MODEL AND DATASET
# ------------------------------------------

@st.cache_resource
def load_ml_model(path):
    return joblib.load(path)


@st.cache_data
def load_dataset(path):
    return pd.read_csv(path)


try:
    model = load_ml_model(str(MODEL_PATH))
    df = load_dataset(str(DATASET_PATH))
except Exception as error:
    st.error(f"Unable to load ML files: {error}")
    st.stop()

FEATURES = [
    "column_load_kN",
    "sbc_kN_m2"
]

TARGET = "footing_length_m"

required_columns = FEATURES + [TARGET]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "Dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

# ------------------------------------------
# 3. MODEL INTRODUCTION
# ------------------------------------------

st.header("1. Machine Learning Methodology")

st.subheader("1.1 Algorithm Used")

st.write(
    """
    The current model uses Random Forest Regression.

    Random Forest is an ensemble machine learning
    algorithm that combines predictions from multiple
    decision trees.

    Each tree learns patterns from training examples,
    and the final regression prediction is obtained
    by averaging the individual tree predictions.

    The current FOOTOPT AI model predicts a preliminary
    square footing side length using two inputs:
    column service load and allowable soil bearing pressure.
    """
)

st.subheader("1.2 Input Features and Target")

feature_table = pd.DataFrame({
    "Variable": [
        "Column Service Load",
        "Allowable Soil Bearing Pressure",
        "Footing Side Length"
    ],
    "Dataset Column": [
        "column_load_kN",
        "sbc_kN_m2",
        "footing_length_m"
    ],
    "Unit": [
        "kN",
        "kN/m²",
        "m"
    ],
    "Role": [
        "Input Feature",
        "Input Feature",
        "Prediction Target"
    ]
})

st.dataframe(
    feature_table,
    hide_index=True,
    use_container_width=True
)

# ------------------------------------------
# 4. DATASET INFORMATION
# ------------------------------------------

st.header("2. Dataset Information")

d1, d2, d3 = st.columns(3)

d1.metric(
    "Dataset Records",
    f"{len(df):,}"
)

d2.metric(
    "Input Features",
    len(FEATURES)
)

d3.metric(
    "Target Variables",
    1
)

st.subheader("2.1 Dataset Generation Method")

st.write(
    """
    The present dataset is synthetic.

    Its target footing side lengths were generated
    from a simplified analytical area-sizing equation,
    rather than from independently verified structural
    designs or measured field data.
    """
)

st.latex(
    r"A_{req} = \frac{P}{q_{allow}}"
)

st.latex(
    r"B_{theoretical} = \sqrt{\frac{P}{q_{allow}}}"
)

st.latex(
    r"B_{target} = "
    r"\frac{\lceil 10 B_{theoretical} \rceil}{10}"
)

st.write(
    "The target side length is rounded upward "
    "to the next 0.1 m."
)

st.info(
    "The ML model learns an approximation of this "
    "synthetic sizing relationship. High accuracy "
    "on this dataset does not demonstrate accuracy "
    "for real-world structural footing design."
)

st.subheader("2.2 Dataset Preview")

st.dataframe(
    df[required_columns].head(10),
    hide_index=True,
    use_container_width=True
)

st.subheader("2.3 Dataset Statistics")

st.dataframe(
    df[required_columns].describe().round(3),
    use_container_width=True
)

# ------------------------------------------
# 5. PREDICTION FORM
# ------------------------------------------

st.header("3. Footing Dimension Prediction")

with st.form("professional_ml_prediction"):

    c1, c2 = st.columns(2)

    with c1:
        load = st.number_input(
            "Column Service Load, P (kN)",
            min_value=1.0,
            value=1000.0,
            step=50.0
        )

    with c2:
        sbc = st.number_input(
            "Allowable Soil Bearing Pressure (kN/m²)",
            min_value=1.0,
            value=200.0,
            step=10.0
        )

    predict_button = st.form_submit_button(
        "Predict Footing Dimension"
    )

if predict_button:

    # Keep the same feature names and order
    input_data = pd.DataFrame(
        [[load, sbc]],
        columns=FEATURES
    )

    try:
        ml_side = float(
            model.predict(input_data)[0]
        )
    except Exception as error:
        st.error(f"Prediction failed: {error}")
        st.stop()

    # Analytical reference
    required_area = load / sbc

    theoretical_side = math.sqrt(required_area)

    analytical_side = (
        math.ceil(
            theoretical_side * 10 - 1e-10
        ) / 10
    )

    absolute_error = abs(
        ml_side - analytical_side
    )

    percentage_error = (
        absolute_error / analytical_side * 100
    )

    st.subheader("3.1 Prediction Results")

    p1, p2, p3 = st.columns(3)

    p1.metric(
        "ML Predicted Side",
        f"{ml_side:.3f} m"
    )

    p2.metric(
        "Analytical Side",
        f"{analytical_side:.3f} m"
    )

    p3.metric(
        "Absolute Difference",
        f"{absolute_error:.3f} m"
    )

    st.subheader("3.2 Analytical Calculation")

    st.latex(
        r"A_{req} = \frac{P}{q_{allow}}"
    )

    st.latex(
        rf"A_{{req}} = "
        rf"\frac{{{load:.2f}}}{{{sbc:.2f}}}"
        rf" = {required_area:.3f}\ \mathrm{{m^2}}"
    )

    st.latex(
        rf"B_{{theoretical}} = "
        rf"\sqrt{{{required_area:.3f}}}"
        rf" = {theoretical_side:.3f}\ \mathrm{{m}}"
    )

    st.write(
        f"Analytical side rounded upward to 0.1 m "
        f"= {analytical_side:.2f} m."
    )

    st.subheader("3.3 Prediction Comparison")

    comparison_df = pd.DataFrame({
        "Method": [
            "Random Forest Prediction",
            "Analytical Sizing Equation"
        ],
        "Footing Side (m)": [
            ml_side,
            analytical_side
        ]
    })

    st.dataframe(
        comparison_df.round(4),
        hide_index=True,
        use_container_width=True
    )

    st.bar_chart(
        comparison_df.set_index("Method")
    )

    st.write(
        f"Absolute difference = {absolute_error:.4f} m"
    )

    st.write(
        f"Percentage difference = {percentage_error:.2f}%"
    )

    if (
        load < df[FEATURES[0]].min()
        or load > df[FEATURES[0]].max()
        or sbc < df[FEATURES[1]].min()
        or sbc > df[FEATURES[1]].max()
    ):
        st.warning(
            "One or more inputs are outside the "
            "training dataset range. ML prediction "
            "may be less reliable."
        )

    st.warning(
        "The predicted side length is an ML estimate, "
        "not an adopted design dimension. "
        "Do not use it directly for construction."
    )

# ------------------------------------------
# 6. MODEL EVALUATION
# ------------------------------------------

st.header("4. Model Evaluation")

st.write(
    """
    Model evaluation measures how closely the trained
    Random Forest reproduces the synthetic target values.

    For a defensible evaluation, predictions should be
    calculated on data that was not used during training.
    """
)

st.subheader("4.1 Evaluation Metrics")

st.latex(
    r"MAE = \frac{1}{n}"
    r"\sum_{i=1}^{n}|y_i-\hat{y}_i|"
)

st.write(
    "Mean Absolute Error (MAE) measures the "
    "average absolute prediction difference, in metres."
)

st.latex(
    r"RMSE = \sqrt{\frac{1}{n}"
    r"\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}"
)

st.write(
    "Root Mean Squared Error (RMSE) gives "
    "greater weight to larger prediction errors."
)

st.latex(
    r"R^2 = 1 - "
    r"\frac{\sum_i(y_i-\hat{y}_i)^2}"
    r"{\sum_i(y_i-\bar{y})^2}"
)

st.write(
    "R² measures how much of the variation "
    "in the evaluation targets is explained "
    "by the model."
)

st.subheader("4.2 Evaluation on Available Dataset")

st.warning(
    "The metrics below are calculated on the "
    "currently available dataset. Because the "
    "original training split is not stored here, "
    "these are NOT confirmed held-out test metrics. "
    "They may be optimistic if training records "
    "are included."
)

try:
    X = df[FEATURES]
    y = df[TARGET]

    predictions = model.predict(X)

    mae = mean_absolute_error(
        y, predictions
    )

    rmse = math.sqrt(
        mean_squared_error(y, predictions)
    )

    r2 = r2_score(
        y, predictions
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Dataset MAE",
        f"{mae:.4f} m"
    )

    m2.metric(
        "Dataset RMSE",
        f"{rmse:.4f} m"
    )

    m3.metric(
        "Dataset R²",
        f"{r2:.4f}"
    )

    evaluation_df = pd.DataFrame({
        "Actual Target (m)": y,
        "Predicted (m)": predictions,
        "Absolute Error (m)": np.abs(
            y.to_numpy() - predictions
        )
    })

    st.subheader("4.3 Prediction Error Table")

    st.dataframe(
        evaluation_df.head(20).round(4),
        hide_index=True,
        use_container_width=True
    )

    st.subheader("4.4 Actual vs Predicted")

    chart_df = evaluation_df[
        ["Actual Target (m)", "Predicted (m)"]
    ].head(100)

    st.line_chart(
        chart_df.reset_index(drop=True)
    )

    st.caption(
        "The chart shows the first 100 dataset records. "
        "It is not an independent test-set evaluation."
    )

except Exception as error:
    st.error(
        f"Model evaluation could not be completed: {error}"
    )

# ------------------------------------------
# 7. INTERPRETATION
# ------------------------------------------

st.header("5. Engineering Interpretation")

st.write(
    """
    The Random Forest model provides a data-driven
    estimate of preliminary square footing dimensions.

    The analytical equation provides the reference
    target used to generate the synthetic dataset.

    The comparison demonstrates whether machine
    learning can approximate this selected numerical
    relationship.

    The current model does not independently evaluate
    bending capacity, shear capacity, reinforcement,
    settlement, or complete foundation safety.
    """
)

st.header("6. Limitations and Future Improvements")

st.markdown(
    """
    - Record and evaluate a reproducible held-out test set.
    - Compare Random Forest with other regression models.
    - Introduce independently validated engineering cases.
    - Expand input features where technically justified.
    - Evaluate uncertainty and out-of-range predictions.
    - Integrate verified structural design constraints.
    """
)

st.divider()

st.caption(
    "FOUNDAX AI | Machine Learning Research Module"
)

from download_model import ensure_model

ensure_model()

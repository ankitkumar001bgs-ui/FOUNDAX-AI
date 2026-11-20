"""College proposal Phase 5: ML model benchmarking on the synthetic footing dataset."""
from pathlib import Path
import pandas as pd
import streamlit as st
from ml_comparison_engine import TARGETS, evaluate_models

st.title("ML Model Comparison & Validation")
st.caption("College proposal: Linear Regression · Random Forest · XGBoost · ANN | Reproducible held-out evaluation")
st.warning("This is a synthetic-data benchmark, NOT validation on real building footing designs or proof of IS 456 compliance. High R² alone does not establish structural safety.")
DATA = Path(__file__).resolve().parents[1] / "dataset" / "isolated_footing_dataset.csv"
if not DATA.exists():
    st.error("Dataset missing: dataset/isolated_footing_dataset.csv")
    st.stop()

df = pd.read_csv(DATA)
st.metric("Available synthetic records", f"{len(df):,}")
with st.expander("Dataset description and leakage controls", expanded=False):
    st.write("Inputs: column_load_kN and sbc_kN_m2. Targets: footing_length_m, footing_breadth_m, or required_area_m2. Each model uses only the two input variables, not the other derived target columns.")
    st.dataframe(df.head(12), use_container_width=True)
    st.info("The synthetic outputs are closely related to the sizing formula A = P/SBC; model scores measure imitation of this dataset, not generalization to real-world structural designs.")

c1, c2, c3 = st.columns(3)
with c1:
    target = st.selectbox("Prediction target", TARGETS, format_func=lambda s: {"footing_length_m": "Footing length (m)", "footing_breadth_m": "Footing breadth (m)", "required_area_m2": "Required area (m²)"}[s])
with c2:
    test_fraction = st.slider("Test fraction", 0.15, 0.35, 0.20, 0.05)
with c3:
    seed = st.number_input("Random seed", min_value=0, max_value=99999, value=42, step=1)
include_xgboost = st.checkbox("Include XGBoost (optional dependency)", value=True)

@st.cache_data(show_spinner=False)
def run_comparison(target_name, fraction, random_seed, xgb_enabled):
    return evaluate_models(pd.read_csv(DATA), target_name, fraction, random_seed, xgb_enabled)

if st.button("Train & Compare Models", type="primary"):
    with st.spinner("Training and evaluating models on held-out data..."):
        try:
            st.session_state["ml_benchmark_result"] = run_comparison(target, test_fraction, int(seed), include_xgboost)
            st.session_state["ml_benchmark_settings"] = (target, test_fraction, int(seed), include_xgboost)
        except Exception as exc:
            st.error(f"Benchmark failed: {exc}")

settings = (target, test_fraction, int(seed), include_xgboost)
if st.session_state.get("ml_benchmark_settings") != settings:
    st.info("Select the settings and click **Train & Compare Models** to calculate real metrics.")
    st.stop()
result = st.session_state["ml_benchmark_result"]
st.subheader("Held-out test results")
st.write(f"Training rows: **{result['train_count']:,}** | Test rows: **{result['test_count']:,}** | Excluded invalid rows: **{result['dropped']:,}**")
st.dataframe(result["metrics"].style.format({"R²": "{:.4f}", "RMSE": "{:.4f}", "MAE": "{:.4f}"}), use_container_width=True, hide_index=True)
st.caption("R²: coefficient of determination (higher is better). RMSE: root mean squared error; MAE: mean absolute error (both lower are better, in target units). These are test-set metrics, not cross-validation.")
st.download_button("Download metrics CSV", result["metrics"].to_csv(index=False), "foundax_ml_model_metrics.csv", "text/csv")
for note in result["notes"]:
    st.warning(note)

st.subheader("Actual vs Predicted")
chosen = st.selectbox("Model to inspect", result["metrics"]["Model"].tolist())
plot_df = result["predictions"][["Actual", chosen]].rename(columns={chosen: "Predicted"})
st.scatter_chart(plot_df, x="Actual", y="Predicted", use_container_width=True)
st.download_button("Download test predictions CSV", result["predictions"].to_csv(index=False), "foundax_ml_test_predictions.csv", "text/csv")

st.subheader("Feature importance (held-out permutation)")
st.caption("Increase in test MAE after shuffling each input. Larger positive values indicate stronger reliance on that feature; values are not causal effects.")
st.dataframe(result["importance"][chosen], use_container_width=True, hide_index=True)

st.subheader("Interpretation for college report")
best = result["metrics"].iloc[0]
st.write(f"For **{target}**, the lowest test RMSE in this run is from **{best['Model']}**. This is a single fixed train/test split; results depend on the dataset and random seed.")
st.info("Next research work: k-fold cross-validation, comparison with verified hand calculations, independent real-building case studies, and documented IS Code checks. Do not present synthetic-model accuracy as proof of a safe footing design.")

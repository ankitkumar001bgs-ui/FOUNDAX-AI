"""College proposal: cross-validation and conventional sizing baseline."""
from pathlib import Path
import pandas as pd
import streamlit as st
from cross_validation_engine import run_cv
from ml_comparison_engine import TARGETS

st.title("Cross-Validation & Conventional Sizing Comparison")
from formula_reference_guide import show_reference_guide
show_reference_guide("ml")

st.caption("College proposal Phase 6 · Reproducible 5-fold evaluation · Educational research")
st.warning("The dataset is synthetic. This page compares predictions to synthetic targets and the idealized A=P/SBC sizing baseline, NOT to verified structural designs or actual construction costs.")
DATA=Path(__file__).resolve().parents[1]/'dataset'/'isolated_footing_dataset.csv'
if not DATA.exists():
    st.error('Dataset not found.'); st.stop()
df=pd.read_csv(DATA)
st.metric('Dataset rows',f'{len(df):,}')
with st.expander('Methodology and limitations'):
    st.write('Randomized K-fold cross-validation with a fixed seed. Models are trained separately within each fold. Input features are column load and SBC only. The conventional baseline uses A = P/SBC, or B = √(P/SBC) for a square footing. No reinforcement, structural safety, load combinations, geotechnical settlement or real building design is verified here.')
    st.write('Target lengths in this dataset may include rounding and synthetic generation rules. The baseline is therefore a mathematical reference, not a full conventional engineered design.')
col1,col2,col3=st.columns(3)
with col1:
    target=st.selectbox('Target',TARGETS,format_func=lambda x:{'required_area_m2':'Required area (m²)','footing_length_m':'Footing length (m)','footing_breadth_m':'Footing breadth (m)'}[x])
with col2:
    folds=st.selectbox('Cross-validation folds',[3,5],index=1)
with col3:
    seed=st.number_input('Random seed',min_value=0,max_value=99999,value=42)
xgb=st.checkbox('Include optional XGBoost (slower)',value=False)
@st.cache_data(show_spinner=False)
def compute(target,folds,seed,xgb):
    return run_cv(pd.read_csv(DATA),target,folds,int(seed),xgb)
settings=(target,folds,int(seed),xgb)
if st.button('Run Cross-Validation',type='primary'):
    with st.spinner('Evaluating each model across folds...'):
        try:
            st.session_state['phase6_result']=compute(*settings)
            st.session_state['phase6_settings']=settings
        except Exception as exc:
            st.error(f'Cross-validation failed: {exc}')
if st.session_state.get('phase6_settings')!=settings:
    st.info('Click **Run Cross-Validation** to calculate metrics.'); st.stop()
res=st.session_state['phase6_result']
st.write(f"Valid rows: **{res['valid_rows']:,}** · Excluded: **{res['dropped']:,}**")
st.subheader('Mean and variation across folds')
st.dataframe(res['summary'].style.format({k:'{:.4f}' for k in res['summary'].columns if k!='Model'}),hide_index=True,use_container_width=True)
st.caption('R² higher is better; RMSE and MAE lower are better. Standard deviations show variation between folds, not confidence intervals.')
st.subheader('Fold-by-fold results')
st.dataframe(res['folds'],hide_index=True,use_container_width=True)
st.download_button('Download summary CSV',res['summary'].to_csv(index=False),'foundax_phase6_cv_summary.csv','text/csv')
st.download_button('Download fold results CSV',res['folds'].to_csv(index=False),'foundax_phase6_cv_folds.csv','text/csv')
for note in res['notes']: st.warning(note)
st.subheader('College proposal status')
st.success('K-fold cross-validation and idealized conventional sizing baseline implemented.')
st.info('Still required: independent hand-calculation verification, real-building footing drawings/load schedules, settlement and code checks, and actual cost comparison. No cost-saving percentage is asserted here.')

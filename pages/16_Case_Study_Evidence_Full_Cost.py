"""User-supplied case-study quantities and evidence audit; no safety certification."""
import pandas as pd
import streamlit as st

st.title('Case Study Evidence & Full Cost Worksheet')
from formula_reference_guide import show_reference_guide
show_reference_guide("cost")

st.caption('Phase 8 | Document actual inputs, compare quantities and identify missing engineering verification')
st.warning('Costs here are estimates based on USER-ENTERED quantities. The app does not calculate structural adequacy, approve reinforcement, or certify an optimized design. Lower cost is NOT proven savings.')

st.subheader('1. Case-study identification and source evidence')
building = st.text_input('Real building name / anonymized case-study ID')
references = {
    'Actual footing drawing and revision': st.text_input('Drawing number / revision'),
    'Column load schedule': st.text_input('Load schedule reference'),
    'Soil investigation / SBC report': st.text_input('Soil report reference'),
    'Reinforcement schedule / bar bending schedule': st.text_input('Reinforcement schedule reference'),
    'Structural design verification': st.text_input('Independent structural verification reference'),
    'Quantity / rate evidence': st.text_input('BOQ / rate reference'),
}
provided = sum(bool(v.strip()) for v in references.values())
st.progress(provided/len(references))
st.write(f'Source references entered: {provided}/{len(references)} (user supplied; authenticity not verified)')
st.dataframe(pd.DataFrame([{'Required evidence': k, 'Status': 'REFERENCE ENTERED — UNVERIFIED' if v.strip() else 'MISSING', 'Reference': v or ''} for k,v in references.items()]), hide_index=True, use_container_width=True)

st.subheader('2. Unit rates')
a,b,c,d=st.columns(4)
with a: concrete_rate=st.number_input('Concrete (INR/m³)',min_value=0.0,value=7000.0)
with b: steel_rate=st.number_input('Rebar steel (INR/kg)',min_value=0.0,value=70.0)
with c: excavation_rate=st.number_input('Excavation (INR/m³)',min_value=0.0,value=400.0)
with d: formwork_rate=st.number_input('Formwork (INR/m²)',min_value=0.0,value=650.0)

st.subheader('3. Actual drawing versus proposed alternative — editable quantities')
cols=['Footing ID','Actual concrete (m³)','Actual steel (kg)','Actual excavation (m³)','Actual formwork (m²)','Alternative concrete (m³)','Alternative steel (kg)','Alternative excavation (m³)','Alternative formwork (m²)']
example=pd.DataFrame([['C1',2.0,150.0,5.0,4.0,1.9,145.0,4.8,3.8]],columns=cols)
st.caption('Example row is fictional and illustrative. Replace ALL values with documented project quantities. Alternative quantities must be independently justified and verified.')
upload=st.file_uploader('Upload quantities CSV',type='csv',key='phase8csv')
if upload is not None:
    try:
        uploaded=pd.read_csv(upload)
        missing=[c for c in cols if c not in uploaded.columns]
        if missing: st.error('CSV missing: '+', '.join(missing))
        else: example=uploaded[cols]
    except Exception as e: st.error(f'CSV could not be read: {e}')
st.download_button('Download blank CSV template',pd.DataFrame(columns=cols).to_csv(index=False),'foundax_phase8_quantity_template.csv',mime='text/csv')
rows=st.data_editor(example,num_rows='dynamic',hide_index=True,use_container_width=True,key='phase8table')

st.subheader('4. Calculate documented cost comparison')
if st.button('Calculate quantities and cost',type='primary'):
    issues=[]
    if rows.empty: issues.append('Enter at least one footing.')
    ids=rows['Footing ID'].astype(str).str.strip() if not rows.empty else []
    if len(ids) != len(set(ids)) or any(not x or x.lower()=='nan' for x in ids): issues.append('Footing IDs must be unique and nonblank.')
    numeric=cols[1:]
    values=rows.copy()
    for col in numeric:
        values[col]=pd.to_numeric(values[col],errors='coerce')
        if values[col].isna().any() or (values[col]<0).any() or (~values[col].map(lambda v: pd.notna(v) and float(v)<float('inf'))).any():
            issues.append(f'{col}: enter finite, nonnegative quantities in every row.')
    if issues:
        for item in issues: st.error(item)
    else:
        rates={'concrete':concrete_rate,'steel':steel_rate,'excavation':excavation_rate,'formwork':formwork_rate}
        for prefix in ('Actual','Alternative'):
            values[f'{prefix} cost (INR)']=(values[f'{prefix} concrete (m³)']*rates['concrete']+values[f'{prefix} steel (kg)']*rates['steel']+values[f'{prefix} excavation (m³)']*rates['excavation']+values[f'{prefix} formwork (m²)']*rates['formwork']).round(2)
        values['Unverified cost difference (INR)']=(values['Actual cost (INR)']-values['Alternative cost (INR)']).round(2)
        st.dataframe(values,hide_index=True,use_container_width=True)
        actual=float(values['Actual cost (INR)'].sum()); alternative=float(values['Alternative cost (INR)'].sum())
        x,y,z=st.columns(3)
        x.metric('Documented actual estimate',f'INR {actual:,.0f}')
        y.metric('Alternative estimate',f'INR {alternative:,.0f}')
        z.metric('UNVERIFIED difference',f'INR {actual-alternative:,.0f}')
        if not all(v.strip() for v in references.values()): st.warning('Case-study evidence incomplete. Add source references before claiming a documented real-building comparison.')
        st.error('Structural adequacy of the alternative is NOT established. This is NOT an optimized, code-approved design or a verified saving.')
        st.download_button('Download cost comparison CSV',values.to_csv(index=False).encode('utf-8'),'foundax_phase8_full_cost_comparison.csv',mime='text/csv')
        evidence=pd.DataFrame([{'Building ID':building or 'NOT PROVIDED','Required evidence':k,'Reference':v or 'MISSING','Verification':'NOT INDEPENDENTLY VERIFIED'} for k,v in references.items()])
        st.download_button('Download evidence register CSV',evidence.to_csv(index=False).encode('utf-8'),'foundax_phase8_evidence_register.csv',mime='text/csv')

st.info('Next verification: reconcile real quantities with drawings and BOQ; confirm load combinations, SBC/settlement, bending, one-way/punching shear, steel detailing and engineer review. Do not use this worksheet for construction decisions.')

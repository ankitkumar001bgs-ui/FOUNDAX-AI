import streamlit as st
import pandas as pd
from capacity_screening import calculate

st.title("Real Building — Reinforcement & Capacity Screening")
from formula_reference_guide import show_reference_guide
show_reference_guide("isolated")

st.error("EDUCATIONAL SCREENING ONLY — not an IS 456 compliance certificate or construction design. Engineer-supplied permissible stress limits and x_u limit must be independently verified from the applicable code and project conditions. No settlement, anchorage, minimum steel, crack control, eccentricity, or full detailing verification is performed.")
st.markdown("**Scope:** Interior, concentric rectangular isolated footing with uniform factored soil pressure and full contact. One-way and punching shear *stress demand* is compared against **user-supplied limits**, not auto-derived IS 456 capacity.")
with st.expander("Equations and conventions"):
    st.markdown(r"""For each direction: projection $a=(B-c)/2$, moment per metre $M_u=q_u a^2/2$, one-way shear per metre $V_u=q_u\max(a-d,0)$. Punching action $V_{up}=q_u[BL-(c_x+d)(c_y+d)]$ and perimeter $b_0=2(c_x+c_y+2d)$ (all lengths in metres for geometry). Stress $\tau_v=V_u/(bd)$, with $b=1000$ mm for one-way shear. For flexure, $x_u=0.87 f_y A_{st}/(0.36 f_{ck}b)$ and $M_{u,R}=0.87 f_y A_{st}(d-0.42x_u)$. This is a simplified singly reinforced rectangular-section calculation. **Minimum steel, max spacing, development length, two-way reinforcement arrangement, strength reduction and code applicability need separate verification.**""")
st.subheader("1. Building evidence")
c1,c2=st.columns(2)
with c1:building=st.text_input("Building / case study ID"); drawing=st.text_input("Drawing / load schedule reference")
with c2:combination=st.text_input("Factored load combination reference"); soil=st.text_input("Soil investigation reference")
st.subheader("2. Verified input limits")
st.warning("Enter allowable one-way shear stress, allowable punching stress and limiting x_u/d ONLY after verifying them against the applicable code, material grade, reinforcement percentage and project conditions. These are NOT calculated by this page.")
c1,c2,c3=st.columns(3)
with c1:tau_one=st.number_input("Verified one-way shear stress limit (N/mm²)",min_value=0.01,value=0.35,step=0.01)
with c2:tau_punch=st.number_input("Verified punching shear stress limit (N/mm²)",min_value=0.01,value=1.0,step=0.05)
with c3:xu_limit=st.number_input("Verified limiting x_u/d ratio",min_value=0.01,max_value=0.99,value=0.46,step=0.01)
st.caption("The displayed defaults are illustrative placeholders, NOT verified IS Code values. Replace with project-appropriate checked limits.")
st.subheader("3. Editable footing schedule")
cols=['Footing ID','B (m)','L (m)','cx (m)','cy (m)','D (mm)','d (mm)','Factored P (kN)','Factored q (kN/m²)','fck (N/mm²)','fy (N/mm²)','Bar diameter (mm)','Bar spacing (mm)']
sample=pd.DataFrame([['DEMO-F1',2.5,2.5,0.4,0.4,500.,420.,1200.,192.,25.,500.,16.,150.]],columns=cols)
upload=st.file_uploader('Upload footing schedule CSV',type='csv',key='cap_csv')
if upload is not None:
    try:
        data=pd.read_csv(upload)
        missing=[c for c in cols if c not in data.columns]
        if missing:st.error('Missing columns: '+', '.join(missing));data=sample
        else:data=data[cols]
    except Exception as exc:st.error(str(exc));data=sample
else:data=sample
edited=st.data_editor(data,num_rows='dynamic',hide_index=True,use_container_width=True,key='cap_editor')
st.download_button('Download blank input template',pd.DataFrame(columns=cols).to_csv(index=False).encode(),'foundax_capacity_input_template.csv','text/csv')
if st.button('Calculate reinforcement and capacity screening',type='primary'):
    errors=[];out=[];ids=set()
    if edited.empty:errors.append('Add at least one footing.')
    for i,r in edited.iterrows():
        fid=str(r['Footing ID']).strip()
        if not fid or fid.lower()=='nan' or fid in ids:errors.append(f'Row {i+1}: missing/duplicate footing ID');continue
        ids.add(fid)
        try:
            values=[float(r[c]) for c in cols[1:]]
            result=calculate(*values,tau_one,tau_punch,xu_limit)
            out.append({'Footing ID':fid,**{k:(round(v,3) if isinstance(v,float) else v) for k,v in result.items()}})
        except (ValueError,TypeError,OverflowError) as exc:errors.append(f'Row {i+1} ({fid}): {exc}')
    if errors:
        for err in errors:st.error(err)
        st.info('Correct input errors before exporting results.')
    else:
        df=pd.DataFrame(out);st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button('Download screening worksheet CSV',df.to_csv(index=False).encode(),'foundax_capacity_screening.csv','text/csv')
        if not all([building.strip(),drawing.strip(),combination.strip(),soil.strip()]):st.warning('Real-building evidence is incomplete: building ID, drawing, load combination and soil report are required.')
        st.warning('WITHIN INPUT LIMITS is NOT a code-compliant or safe design approval. Check minimum steel, development length, detailing, settlement, bearing, all load cases and independently verify all stress limits before any engineering use.')
st.subheader('4. Remaining college-project verification')
st.markdown('Manual worked examples and independent software comparison; verified IS 456 provisions and shear limits; detailing and development length; eccentric and combined footing checks; geotechnical settlement; real building case study evidence and engineering review.')

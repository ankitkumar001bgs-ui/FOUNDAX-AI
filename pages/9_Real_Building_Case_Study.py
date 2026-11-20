"""Real-building footing case-study intake and preliminary schedule.
No claim of construction-ready structural design or IS-code compliance.
"""
import io
import math
import pandas as pd
import streamlit as st

st.title('Real Building Footing Case Study')
from formula_reference_guide import show_reference_guide
show_reference_guide("combined")

st.caption('College proposal: documented real-building case study | Preliminary engineering screening only')
st.warning('This tool does NOT produce a construction-ready footing design. Soil settlement, eccentric loading, load combinations, structural bending/shear, reinforcement and detailed IS-code compliance require verified engineering assessment.')

with st.expander('1. Building identification and source evidence', expanded=True):
    a,b=st.columns(2)
    with a:
        building=st.text_input('Building name / case-study ID', placeholder='Enter real building reference')
        location=st.text_input('Location', placeholder='City / district')
        building_type=st.selectbox('Building use',['Residential','Commercial','Institutional','Industrial','Other'])
        floors=st.number_input('Number of storeys',min_value=1,value=2)
    with b:
        source=st.text_input('Source of structural drawings / data',placeholder='Drawing number / engineer / date')
        soil_source=st.text_input('Soil investigation / SBC source',placeholder='Report number / date')
        reviewed_by=st.text_input('Responsible engineer / reviewer (optional)')
        st.caption('Do not enter private owner contact details. Obtain permission before using real project records.')

st.subheader('2. Soil, geometry and material inputs')
c1,c2,c3=st.columns(3)
with c1:
    sbc=st.number_input('Allowable SBC (kN/m²)',min_value=1.0,value=200.0)
    soil=st.selectbox('Soil description',['Not provided','Sand','Clay','Silt','Gravel','Mixed / other'])
    depth=st.number_input('Foundation embedment depth (m)',min_value=0.0,value=1.5)
with c2:
    concrete=st.selectbox('Concrete grade',['M20','M25','M30','M35','Other'])
    steel=st.selectbox('Steel grade',['Fe415','Fe500','Other'])
    clearance=st.number_input('Nominal dimension rounding increment (m)',min_value=0.05,max_value=0.5,value=0.1,step=0.05)
with c3:
    allowance=st.number_input('Illustrative additional service load allowance (%)',min_value=0.0,max_value=30.0,value=10.0,step=1.0,help='Screening assumption only; not a substitute for footing self-weight or overburden calculation.')
    concrete_rate=st.number_input('Concrete rate (INR/m³)',min_value=0.0,value=7000.0)
    excavation_rate=st.number_input('Excavation rate (INR/m³)',min_value=0.0,value=400.0)

st.subheader('3. Editable column / footing schedule')
st.write('Enter actual service column loads, dimensions and available footprint. Optional drawing dimensions allow a direct area/pressure comparison. All lengths are in metres.')
columns=['Column ID','Service Load (kN)','Column Width (m)','Column Length (m)','X (m)','Y (m)','Available Width (m)','Available Length (m)','Drawing Width (m)','Drawing Length (m)','Drawing Thickness (m)']
example=pd.DataFrame([['C1',650.0,0.30,0.45,0.0,0.0,None,None,None,None,None],['C2',850.0,0.40,0.45,4.0,0.0,None,None,None,None,None]],columns=columns)
st.caption('Example rows are fictional templates, NOT real building data. Replace or delete them before documenting a real case study.')
upload=st.file_uploader('Optional: Upload column schedule CSV',type=['csv'])
if upload is not None:
    try:
        raw=pd.read_csv(upload)
        missing=[x for x in columns[:4] if x not in raw.columns]
        if missing:
            st.error('Missing required CSV columns: '+', '.join(missing))
            raw=example
        else:
            for name in columns:
                if name not in raw.columns:raw[name]=None
            raw=raw[columns]
    except Exception as e:
        st.error(f'CSV could not be read: {e}')
        raw=example
else:raw=example
edited=st.data_editor(raw,num_rows='dynamic',hide_index=True,use_container_width=True,key='building_schedule')
st.download_button('Download blank CSV template',pd.DataFrame(columns=columns).to_csv(index=False).encode('utf-8'),'foundax_case_study_template.csv','text/csv')

st.subheader('4. Preliminary analysis')
if st.button('Analyze building footing schedule',type='primary'):
    errors=[]; results=[]
    if not building.strip(): errors.append('Enter a real building name or case-study ID.')
    if not source.strip(): st.info('Structural drawing/data source not supplied: real-building provenance remains unverified.')
    if not soil_source.strip(): st.info('SBC report reference not supplied: bearing capacity must be verified.')
    if edited.empty:errors.append('Enter at least one column.')
    ids=set()
    for idx,record in edited.iterrows():
        label=str(record.get('Column ID','')).strip()
        if not label or label.lower()=='nan':errors.append(f'Row {idx+1}: Column ID is required.');continue
        if label in ids:errors.append(f'Duplicate Column ID: {label}');continue
        ids.add(label)
        try:
            load=float(record['Service Load (kN)']);cw=float(record['Column Width (m)']);cl=float(record['Column Length (m)'])
            if not all(math.isfinite(v) and v>0 for v in [load,cw,cl]):raise ValueError('load and dimensions must be positive')
            req=load*(1+allowance/100)/sbc
            side=math.ceil(math.sqrt(req)/clearance-1e-10)*clearance
            side=round(side,3)
            pressure=load*(1+allowance/100)/(side*side)
            notes=[]
            if side<=max(cw,cl):notes.append('Footing does not project beyond column')
            for axis,needed in [('Width',side),('Length',side)]:
                val=record.get(f'Available {axis} (m)')
                if pd.notna(val) and str(val).strip():
                    if float(val)<=0:notes.append(f'Invalid available {axis.lower()}')
                    elif needed>float(val):notes.append(f'Exceeds available {axis.lower()}; investigate combined/strap/other solution')
            dw=record.get('Drawing Width (m)');dl=record.get('Drawing Length (m)')
            drawing_area=None;drawing_pressure=None
            if pd.notna(dw) and pd.notna(dl) and str(dw).strip() and str(dl).strip():
                if float(dw)>0 and float(dl)>0:
                    drawing_area=float(dw)*float(dl)
                    drawing_pressure=load*(1+allowance/100)/drawing_area
                    if drawing_pressure>sbc:notes.append('Drawing footprint exceeds entered allowable SBC under screening assumption')
                else:notes.append('Invalid drawing dimensions')
            results.append({'Column ID':label,'Service Load (kN)':load,'Required Area (m²)':round(req,3),'Suggested Square Side (m)':side,'Suggested Area (m²)':round(side*side,3),'Screening Pressure (kN/m²)':round(pressure,2),'Entered SBC (kN/m²)':sbc,'Drawing Area (m²)':round(drawing_area,3) if drawing_area else None,'Drawing Pressure (kN/m²)':round(drawing_pressure,2) if drawing_pressure else None,'Status':'REVIEW REQUIRED' if notes else 'PRELIMINARY ONLY','Notes':'; '.join(notes) if notes else 'Detailed structural and geotechnical checks pending'})
        except (ValueError,TypeError,OverflowError) as e:errors.append(f'Row {idx+1} ({label}): invalid numeric data ({e}).')
    if errors:
        for e in errors:st.error(e)
        st.info('Correct the entries and run the analysis again. No results were accepted.')
    else:
        output=pd.DataFrame(results)
        st.success(f'Preliminary schedule calculated for {len(output)} column(s). Not an approved structural design.')
        st.dataframe(output,use_container_width=True,hide_index=True)
        st.download_button('Download footing screening schedule CSV',output.to_csv(index=False).encode('utf-8'),'foundax_real_building_footing_schedule.csv','text/csv')
        st.markdown('**Calculation basis:** A_required = P_service × (1 + allowance/100) / SBC; square side rounded upward to selected increment. Assumes concentric vertical load and uniform bearing. This is an area screening calculation, not a full footing design.')
        st.markdown('**Outstanding design verification:** site-specific geotechnical report and settlement; dead/live/wind/seismic combinations; eccentricity and uplift; footing thickness, flexure, one-way and punching shear; anchorage and reinforcement detailing; interaction between adjacent footings; construction and durability requirements; relevant Indian Standards checked by a qualified engineer.')
        st.info('Real case study completion requires documented building data, independent hand/design-software comparison and qualified engineering review. No real-world validation is claimed from template entries.')

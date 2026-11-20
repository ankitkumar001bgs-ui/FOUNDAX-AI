import json
import streamlit as st
import pandas as pd
from verification_engine import bearing_check

st.title('Independent Calculation Benchmark')
from formula_reference_guide import show_reference_guide
show_reference_guide("isolated")

st.caption('Transparent hand-calculation comparison for preliminary soil bearing only. Not a structural design certificate.')
st.info('Use service-level loads and an SBC defined on a consistent gross/net basis. Self-weight allowance is an illustrative percentage, not a substitute for actual footing and soil weights.')
with st.form('benchmark_inputs'):
    a,b,c=st.columns(3)
    with a:
        load=st.number_input('Column service load (kN)',min_value=1.0,value=800.0)
        length=st.number_input('Footing length L (m)',min_value=0.1,value=2.2)
        width=st.number_input('Footing width B (m)',min_value=0.1,value=2.2)
    with b:
        sbc=st.number_input('Allowable SBC (kN/m²)',min_value=1.0,value=200.0)
        mx=st.number_input('Service moment Mx (kN·m)',value=0.0)
        my=st.number_input('Service moment My (kN·m)',value=0.0)
    with c:
        allowance=st.number_input('Illustrative additional vertical load (%)',min_value=0.0,max_value=100.0,value=0.0)
        reference=st.text_input('Hand calculation / drawing reference (optional)')
    run=st.form_submit_button('Calculate and compare',type='primary')
if run:
    r=bearing_check(load,length,width,sbc,mx,my,allowance)
    st.subheader('Independent benchmark results')
    m1,m2,m3=st.columns(3)
    m1.metric('Required area (m²)',f"{r['required_area_m2']:.3f}")
    m2.metric('Maximum pressure (kN/m²)',f"{r['maximum_pressure_kn_m2']:.2f}")
    m3.metric('Allowable SBC (kN/m²)',f'{sbc:.2f}')
    if not r['full_contact']:
        st.error('Full-contact assumption fails: calculated minimum pressure is negative. Do not interpret this linear pressure estimate as a valid partial-contact design.')
    elif r['bearing_within_sbc']:
        st.success('Preliminary full-contact bearing-pressure screen passes for these inputs.')
    else:
        st.warning('Preliminary bearing-pressure screen does not pass.')
    st.latex(r'A=LB,\quad q_{avg}=P/A,\quad q_{max/min}=P/A\pm 6|M_y|/(BL^2)\pm 6|M_x|/(LB^2)')
    st.write('**Independent hand calculation comparison**')
    manual=st.number_input('Manually calculated maximum pressure (kN/m²)',min_value=0.0,value=round(r['maximum_pressure_kn_m2'],2),key='manual_qmax')
    diff=manual-r['maximum_pressure_kn_m2']
    st.write(f'Difference (manual − application): **{diff:+.3f} kN/m²**')
    result={**r,'input_load_kn':load,'input_length_m':length,'input_width_m':width,'input_sbc_kn_m2':sbc,
            'input_mx_knm':mx,'input_my_knm':my,'input_allowance_pct':allowance,'drawing_reference':reference,
            'manual_max_pressure_kn_m2':manual,'manual_minus_app_kn_m2':diff,
            'scope':'Educational preliminary bearing benchmark only; structural capacity and settlement unverified'}
    st.download_button('Download benchmark JSON',json.dumps(result,indent=2),file_name='bearing_benchmark.json',mime='application/json')
    st.download_button('Download benchmark CSV',pd.DataFrame([result]).to_csv(index=False),file_name='bearing_benchmark.csv',mime='text/csv')
st.divider()
st.subheader('Required before a real-building case study is complete')
st.write('Actual column load schedule, column dimensions, geotechnical SBC and settlement data, footing drawings, material grades, reinforcement details, hand-calculation sheets, and engineer review. Missing documents must be marked pending, not assumed.')
st.warning('Passing the bearing screen does not verify bending, one-way shear, punching shear, reinforcement anchorage/detailing, combined-footing behavior, or IS 456/IS 1904 compliance.')

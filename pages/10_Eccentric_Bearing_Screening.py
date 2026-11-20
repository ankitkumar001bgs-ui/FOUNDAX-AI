"""Service-load eccentric bearing screening for real-building footing case studies.
NOT a complete footing design; does not verify IS-code compliance.
"""
import math
import pandas as pd
import streamlit as st

st.title("Real Building — Eccentric Bearing Screening")
st.caption("Phase 2 | Load and moment screening for rectangular isolated footing footprints")
st.warning("Preliminary service-level soil pressure screening ONLY. Not structural design or construction approval. The linear full-contact pressure model is invalid when contact tension is predicted. Settlement, load combinations, sliding, overturning, uplift, structural shear/flexure, reinforcement and code compliance are not verified.")

with st.expander("Calculation method and input conventions", expanded=False):
    st.markdown("""For a rigid rectangular footing with vertical service load **P** (kN), plan width **B** (m), length **L** (m), and service moments **Mx**, **My** (kN·m):

- Average pressure: **q₀ = P / (B L)** (kN/m²)
- Eccentricities: **ex = My / P**, **ey = Mx / P** (m)
- Corner pressure: **q = q₀ ± 6 My/(L B²) ± 6 Mx/(B L²)** (kN/m²)
- The four sign combinations give four theoretical corner pressures under the *full-contact linear elastic assumption*.

**Axes:** B is the X dimension, L the Y dimension; My causes pressure variation along X, Mx along Y. Enter signed moments. If any predicted corner pressure is negative, the full-contact assumption fails and this page does **not** calculate a reduced-contact solution. Enter service-level actions consistent with the entered allowable soil bearing pressure. Include footing/soil self-weight and overburden in P when justified by project data; this tool does not add them automatically.""")

sbc=st.number_input("Allowable net/gross bearing pressure from soil report (kN/m²)",min_value=0.1,value=200.0,help="Confirm net/gross basis and relevant load case with the geotechnical engineer.")
source=st.text_input("Soil report / design data reference",placeholder="Report ID, revision and date")
st.caption("Template values below are fictional demonstrations, not a real building case study.")
cols=["Footing ID","P service (kN)","B width X (m)","L length Y (m)","Mx service (kN.m)","My service (kN.m)"]
example=pd.DataFrame([["F1",800.0,2.5,2.5,0.0,0.0],["F2",1000.0,3.0,2.5,35.0,20.0]],columns=cols)
up=st.file_uploader("Upload service load and moment schedule (CSV)",type=["csv"],key="ecc_csv")
if up is not None:
    try:
        incoming=pd.read_csv(up)
        missing=[c for c in cols if c not in incoming.columns]
        if missing:st.error("Missing columns: "+", ".join(missing)); incoming=example
        else:incoming=incoming[cols]
    except Exception as exc:
        st.error(f"CSV could not be read: {exc}");incoming=example
else:incoming=example
edited=st.data_editor(incoming,num_rows="dynamic",hide_index=True,use_container_width=True,key="ecc_table")
st.download_button("Download blank input template",pd.DataFrame(columns=cols).to_csv(index=False).encode(),"foundax_eccentric_input_template.csv","text/csv")

if st.button("Run eccentric bearing screening",type="primary"):
    errors=[];result=[];seen=set()
    if edited.empty:errors.append("Enter at least one footing.")
    for i,r in edited.iterrows():
        fid=str(r["Footing ID"]).strip()
        if not fid or fid.lower()=="nan":errors.append(f"Row {i+1}: Footing ID required");continue
        if fid in seen:errors.append(f"Duplicate footing ID: {fid}");continue
        seen.add(fid)
        try:
            p,b,l,mx,my=[float(r[c]) for c in cols[1:]]
            if not all(math.isfinite(v) for v in (p,b,l,mx,my)) or min(p,b,l)<=0:raise ValueError("P, B, L must be finite and positive; moments finite")
            q0=p/(b*l)
            dx=6*my/(l*b*b)
            dy=6*mx/(b*l*l)
            corner=[q0+sx*dx+sy*dy for sx in (-1,1) for sy in (-1,1)]
            qmin=min(corner);qmax=max(corner)
            ex=my/p;ey=mx/p
            full_contact=qmin>=-1e-9
            status="FULL-CONTACT SCREEN: WITHIN ENTERED SBC" if full_contact and qmax<=sbc+1e-9 else ("REVIEW: POSSIBLE LOSS OF CONTACT" if not full_contact else "REVIEW: EXCEEDS ENTERED SBC")
            result.append({"Footing ID":fid,"P service (kN)":p,"B (m)":b,"L (m)":l,"Mx (kN.m)":mx,"My (kN.m)":my,"ex (m)":round(ex,4),"ey (m)":round(ey,4),"q avg (kN/m²)":round(q0,2),"q min theoretical (kN/m²)":round(qmin,2),"q max theoretical (kN/m²)":round(qmax,2),"Entered SBC (kN/m²)":sbc,"Status":status,"Full contact model applicable":full_contact})
        except (TypeError,ValueError,OverflowError) as exc:errors.append(f"Row {i+1} ({fid}): invalid input — {exc}")
    if errors:
        for error in errors:st.error(error)
        st.info("Fix all input errors and rerun. Results not accepted.")
    else:
        out=pd.DataFrame(result)
        st.dataframe(out,hide_index=True,use_container_width=True)
        st.download_button("Download screening results CSV",out.to_csv(index=False).encode(),"foundax_eccentric_bearing_screening.csv","text/csv")
        st.info("A 'within SBC' screen is not a pass for the footing design. Confirm soil report basis, load combinations, stability, settlement and structural design independently. Negative q min indicates that a different soil-contact analysis is required.")
        if not source.strip():st.warning("Soil report reference missing: do not label these as verified real-building results.")

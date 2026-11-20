"""Educational factored-load action worksheet for isolated pad footing.
This computes simplified demand only, not design capacity or code compliance.
"""
import math
import pandas as pd
import streamlit as st

st.title("Real Building — Structural Demand Worksheet")
st.caption("College proposal | Factored bending, one-way shear and punching shear action estimates")
st.error("NOT a complete or approved footing design. This worksheet estimates actions only. It does not verify IS 456 shear/flexural capacities, anchorage, reinforcement, settlement or IS-code compliance. A qualified engineer must review loads, geometry and calculations.")
st.markdown("Enter **factored vertical action** and a **factored uniform upward soil pressure** that has been independently justified for the governing load combination. Do not substitute service SBC for factored pressure. The model assumes a concentric, centrally loaded rectangular isolated footing with full soil contact; eccentricity, edge/combined footing and nonlinear contact are out of scope.")
with st.expander("Calculation conventions",expanded=False):
    st.markdown("""**B, L** = footing plan dimensions (m); **cx, cy** = column dimensions along B and L (m); **D** = total depth (mm); **d** = assumed effective depth (mm); **qᵤ** = factored uniform upward pressure (kN/m²). Projection **ax=(B−cx)/2**, **ay=(L−cy)/2**.

- Cantilever bending action per metre at column face: **Mux = qᵤ ax²/2**, **Muy = qᵤ ay²/2** (kN·m/m).
- Illustrative one-way shear action per metre at a section **d** from the column face: **Vux = qᵤ max(ax−d,0)** and **Vuy = qᵤ max(ay−d,0)** (kN/m).
- Illustrative two-way punching action for an interior column, perimeter offset **d/2** from column faces: **Vu,p = qᵤ × [B L − (cx+d)(cy+d)]** (kN), only if that entire perimeter is within the footing and the factored pressure/action model is consistent.

These are **action estimates, not pass/fail design checks**. Actual footing design needs load path equilibrium, all load combinations, critical sections, capacity formulae, material factors, reinforcement and detailing checks under the applicable code provisions.""")

st.subheader("1. Evidence and assumptions")
a,b=st.columns(2)
with a:
    building=st.text_input("Building / case-study ID")
    drawing=st.text_input("Structural drawing / load schedule reference")
with b:
    combination=st.text_input("Governing factored load combination / reference")
    reviewer=st.text_input("Engineer / reviewer reference (optional)")

st.subheader("2. Editable footing input schedule")
fields=["Footing ID","B (m)","L (m)","cx (m)","cy (m)","D (mm)","d (mm)","Factored P (kN)","Factored q (kN/m²)"]
template=pd.DataFrame([["F1",2.5,2.5,0.4,0.4,500.0,420.0,1200.0,192.0]],columns=fields)
st.caption("F1 is fictional demonstration data. Delete or replace before using a real building case study. Factored q is NOT calculated from allowable SBC.")
upload=st.file_uploader("Upload footing inputs (CSV)",type=["csv"],key="structural_csv")
if upload is not None:
    try:
        raw=pd.read_csv(upload)
        missing=[f for f in fields if f not in raw.columns]
        if missing:
            st.error("CSV is missing: "+", ".join(missing));raw=template
        else:raw=raw[fields]
    except Exception as exc:
        st.error(f"CSV could not be read: {exc}");raw=template
else:raw=template
edited=st.data_editor(raw,num_rows="dynamic",hide_index=True,use_container_width=True,key="structural_table")
st.download_button("Download blank input template",pd.DataFrame(columns=fields).to_csv(index=False).encode(),"foundax_structural_demand_template.csv","text/csv")

if st.button("Calculate preliminary structural actions",type="primary"):
    errors=[];results=[];ids=set()
    if edited.empty:errors.append("Enter at least one footing.")
    for index,r in edited.iterrows():
        fid=str(r["Footing ID"]).strip()
        if not fid or fid.lower()=="nan" or fid in ids:
            errors.append(f"Row {index+1}: missing or duplicate Footing ID");continue
        ids.add(fid)
        try:
            B,L,cx,cy,D,d,P,q=[float(r[c]) for c in fields[1:]]
            if not all(math.isfinite(v) and v>0 for v in (B,L,cx,cy,D,d,P,q)):
                raise ValueError("All numeric inputs must be finite and positive")
            if cx>=B or cy>=L:raise ValueError("Column must be smaller than footing in both directions")
            if d>=D:raise ValueError("Effective depth d must be less than total depth D")
            dm=d/1000
            ax=(B-cx)/2;ay=(L-cy)/2
            if cx+dm>=B or cy+dm>=L:raise ValueError("Interior punching control perimeter does not fit within footing")
            # Equilibrium check for the specified factored uniform pressure; user must resolve differences
            q_from_p=P/(B*L)
            difference=abs(q-q_from_p)/max(q,q_from_p)
            mx=q*ax*ax/2;my=q*ay*ay/2
            vx=q*max(ax-dm,0);vy=q*max(ay-dm,0)
            punching=q*(B*L-(cx+dm)*(cy+dm))
            flag=("LOAD/PRESSURE MISMATCH — REVIEW" if difference>0.05 else "DEMANDS ONLY — CAPACITY NOT CHECKED")
            results.append({"Footing ID":fid,"ax (m)":round(ax,3),"ay (m)":round(ay,3),"P/(BL) (kN/m²)":round(q_from_p,2),"Entered qu (kN/m²)":round(q,2),"Mu x (kN.m/m)":round(mx,2),"Mu y (kN.m/m)":round(my,2),"Vu x (kN/m)":round(vx,2),"Vu y (kN/m)":round(vy,2),"Punching Vu (kN)":round(punching,2),"Status":flag})
        except (ValueError,TypeError,OverflowError) as exc:
            errors.append(f"Row {index+1} ({fid}): {exc}")
    if errors:
        for error in errors:st.error(error)
        st.info("No results accepted until all rows are valid.")
    else:
        out=pd.DataFrame(results)
        st.dataframe(out,hide_index=True,use_container_width=True)
        st.download_button("Download structural demand worksheet CSV",out.to_csv(index=False).encode(),"foundax_structural_demand_worksheet.csv","text/csv")
        if not drawing.strip() or not combination.strip():st.warning("Missing source drawing or factored load-combination reference: not a verified real case study.")
        if any(out["Status"].str.contains("MISMATCH")):st.error("Factored P and entered factored q differ by more than 5% for at least one footing. Resolve load balance and pressure assumptions before interpreting actions.")
        st.warning("No design capacities or reinforcement areas have been calculated. Results are preliminary demand estimates only; do not use for construction or claim IS 456 compliance.")

st.subheader("3. Outstanding checks for a complete case study")
st.markdown("- Verified structural actions and load combinations, including moments and lateral loads\n- Soil report, bearing and settlement assessment\n- IS 456 flexure, one-way shear and punching shear **capacity** verification\n- Reinforcement design, minimum steel, development length and detailing\n- Independent manual/software comparison and engineer sign-off")

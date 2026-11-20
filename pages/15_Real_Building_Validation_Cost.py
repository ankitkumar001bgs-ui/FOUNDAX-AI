"""Evidence-aware real-building footing geometry and partial-cost comparison."""
import io
from datetime import date
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from case_study_validation_engine import REQUIRED, compare_footing

st.title('Real Building Validation & Cost Comparison')
from formula_reference_guide import show_reference_guide
show_reference_guide("combined")

st.caption('Phase 7 | College project case-study evidence, geometric bearing screening and partial quantity/cost comparison')
st.warning('This is NOT a complete footing design or a code-compliance certificate. The comparison alternative has no validated thickness, reinforcement, shear, settlement or structural adequacy. Do not use its cost difference as proven savings.')

with st.expander('1. Real building identification and evidence', expanded=True):
    a, b = st.columns(2)
    with a:
        building = st.text_input('Building name / case-study ID')
        location = st.text_input('Building location')
        drawing_ref = st.text_input('Actual footing drawing / revision reference')
    with b:
        soil_ref = st.text_input('Geotechnical / SBC report reference')
        load_ref = st.text_input('Column load schedule reference')
        reviewer = st.text_input('Engineer / reviewer reference (optional)')
    st.caption('Use authorized, anonymized records. References are user-entered, not independently verified by this application.')

st.subheader('2. Soil, assumptions and unit rates')
a, b, c = st.columns(3)
with a:
    sbc = st.number_input('Entered allowable SBC (kN/m²)', min_value=1.0, value=200.0)
    allowance = st.number_input('Illustrative load allowance (%)', min_value=0.0, max_value=30.0, value=10.0)
with b:
    increment = st.number_input('Square-side rounding increment (m)', min_value=0.05, max_value=0.5, value=0.1, step=0.05)
    assumed_thickness = st.number_input('Assumed comparison thickness (m)', min_value=0.1, value=0.45, step=0.05)
with c:
    depth = st.number_input('Assumed excavation depth (m)', min_value=0.1, value=1.5)
    concrete_rate = st.number_input('Concrete unit rate (INR/m³)', min_value=0.0, value=7000.0)
    excavation_rate = st.number_input('Excavation unit rate (INR/m³)', min_value=0.0, value=400.0)
st.info('Cost covers ONLY concrete volume and simple excavation volume. Steel, reinforcement, formwork, backfill, labor, wastage, taxes and site constraints are excluded. The comparison thickness is a user assumption, not a designed thickness.')

st.subheader('3. Actual drawing schedule — editable / CSV upload')
cols = list(REQUIRED)
example = pd.DataFrame([['C1', 650.0, 2.1, 2.1, 0.45], ['C2', 850.0, 2.4, 2.4, 0.50]], columns=cols)
st.caption('The pre-filled rows are FICTIONAL DEMONSTRATION DATA. Replace them with actual documented building data.')
file = st.file_uploader('Upload CSV with these column names', type=['csv'])
raw = example
if file:
    try:
        candidate = pd.read_csv(file)
        missing = [x for x in cols if x not in candidate.columns]
        if missing:
            st.error('Missing CSV columns: ' + ', '.join(missing))
        else:
            raw = candidate[cols]
    except Exception as exc:
        st.error(f'Unable to read CSV: {exc}')
rows = st.data_editor(raw, num_rows='dynamic', hide_index=True, use_container_width=True, key='phase7_footing_table')
st.download_button('Download blank CSV template', pd.DataFrame(columns=cols).to_csv(index=False), 'foundax_real_building_case_template.csv', mime='text/csv')

st.subheader('4. Analyze and document')
if st.button('Calculate case-study comparison', type='primary'):
    problems = []
    if rows.empty:
        problems.append('Add at least one footing row.')
    ids = rows['Column ID'].astype(str).str.strip().tolist() if not rows.empty else []
    if len(ids) != len(set(ids)):
        problems.append('Column IDs must be unique.')
    computed = []
    for i, row in rows.iterrows():
        try:
            computed.append(compare_footing(row, sbc, allowance, increment, assumed_thickness, depth, concrete_rate, excavation_rate))
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            problems.append(f'Row {i + 1}: {exc}')
    if problems:
        for msg in problems:
            st.error(msg)
    else:
        result = pd.DataFrame(computed)
        evidence = bool(building.strip() and drawing_ref.strip() and soil_ref.strip() and load_ref.strip())
        st.success(f'Comparison worksheet calculated for {len(result)} footing(s). Structural approval NOT established.')
        if not evidence:
            st.warning('CASE STUDY EVIDENCE INCOMPLETE: building ID, actual drawing reference, SBC report and load schedule reference are all needed to document a real building case study.')
        else:
            st.info('Source references supplied by user; authenticity and engineering correctness remain unverified.')
        st.dataframe(result, hide_index=True, use_container_width=True)
        drawing_total = result['Drawing Partial Cost (INR)'].sum()
        alternative_total = result['Comparison Partial Cost (INR)'].sum()
        difference = drawing_total - alternative_total
        x, y, z = st.columns(3)
        x.metric('Drawing partial cost', f'₹{drawing_total:,.0f}')
        y.metric('Comparison partial cost', f'₹{alternative_total:,.0f}')
        z.metric('Unverified cost difference', f'₹{difference:,.0f}')
        st.caption('Positive difference indicates a lower partial estimated cost for the UNVERIFIED comparison geometry; it is not a demonstrated saving or an acceptable structural design.')
        st.download_button('Download results CSV', result.to_csv(index=False).encode('utf-8'), 'foundax_phase7_case_comparison.csv', mime='text/csv')

        def make_pdf():
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=38, leftMargin=38, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            story = [Paragraph('FOUNDAX AI — Building Footing Case Study Comparison', styles['Title']), Spacer(1, 12)]
            fields = [('Date', str(date.today())), ('Building / ID', building or 'NOT PROVIDED'), ('Location', location or 'NOT PROVIDED'), ('Drawing reference', drawing_ref or 'NOT PROVIDED'), ('Soil report reference', soil_ref or 'NOT PROVIDED'), ('Load schedule reference', load_ref or 'NOT PROVIDED'), ('Reviewer', reviewer or 'NOT PROVIDED'), ('Evidence status', 'References entered (not independently verified)' if evidence else 'INCOMPLETE')]
            for k, v in fields:
                story.append(Paragraph(f'<b>{k}:</b> {str(v).replace("&", "&amp;").replace("<", "&lt;")}', styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph('Assumptions and scope', styles['Heading2']))
            for line in [f'Allowable SBC: {sbc} kN/m²; illustrative load allowance: {allowance}%.', f'Comparison square side increment: {increment} m; ASSUMED comparison thickness: {assumed_thickness} m.', f'Excavation depth: {depth} m; concrete rate: INR {concrete_rate}/m³; excavation rate: INR {excavation_rate}/m³.', 'Costs EXCLUDE steel, formwork, labor, backfill and other site expenses.', 'Bearing pressure uses simplified concentric service loading; no settlement, eccentricity or structural capacity verification.', 'Not an IS Code compliance certificate. Not suitable for construction.']:
                story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph('Footing-by-footing comparison', styles['Heading2']))
            headers = ['ID', 'Draw. area', 'Comp. area', 'Draw. q', 'Comp. q', 'Cost diff.']
            data = [headers]
            for _, r in result.iterrows():
                data.append([str(r['Column ID']), str(r['Drawing Area (m²)']), str(r['Comparison Area (m²)']), str(r['Drawing Pressure (kN/m²)']), str(r['Comparison Pressure (kN/m²)']), f"{r['Partial Cost Difference (INR)']:,.0f}"])
            table = Table(data, repeatRows=1, hAlign='LEFT', colWidths=[58, 77, 77, 76, 76, 91])
            table.setStyle(TableStyle([('BACKGROUND', (0,0),(-1,0), colors.HexColor('#DCEDEA')), ('GRID', (0,0),(-1,-1), 0.3, colors.grey), ('FONTSIZE',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),6), ('TOPPADDING',(0,0),(-1,-1),6)]))
            story.append(table)
            story.append(Spacer(1, 12))
            story.append(Paragraph(f'Drawing partial cost: INR {drawing_total:,.2f}; comparison partial cost: INR {alternative_total:,.2f}; UNVERIFIED difference: INR {difference:,.2f}.', styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph('Outstanding verification', styles['Heading2']))
            story.append(Paragraph('Actual structural loads and combinations; footing self-weight and overburden; eccentric bearing/uplift; soil settlement; bending, one-way shear, punching shear; reinforcement and anchorage; interaction of nearby foundations; construction detailing; independent engineer review.', styles['Normal']))
            doc.build(story)
            return buf.getvalue()
        st.download_button('Download case-study PDF report', make_pdf(), 'foundax_phase7_case_study_report.pdf', mime='application/pdf')

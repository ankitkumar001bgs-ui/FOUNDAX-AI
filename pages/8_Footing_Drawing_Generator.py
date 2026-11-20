"""FOUNDAX AI | Professional preliminary isolated-footing drawing generator.

All input dimensions are schematic; no structural strength or settlement verification.
"""
from datetime import date
import csv
from io import BytesIO, StringIO
from math import ceil, sqrt
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import streamlit as st
import plotly.graph_objects as go
import numpy as np

try:
    from theme import apply_theme
except ImportError:
    apply_theme = None

st.set_page_config(page_title='FOUNDAX AI | Drawing Generator', layout='wide')
if apply_theme is not None:
    apply_theme()

NAVY = '#19334d'
BLUE = '#236f9c'
PALE = '#dfeaf1'
GRAY = '#66788a'
INK = '#172a3a'


def ceil_to(value, step=0.1):
    return ceil((value - 1e-10) / step) * step


def clean_axis(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('white')
    ax.axis('off')


def dim_h(ax, x1, x2, y_ref, y_dim, text):
    for x in (x1, x2):
        ax.plot([x, x], [y_ref, y_dim + (0.05 if y_dim > y_ref else -0.05)], color=GRAY, lw=.75)
    ax.annotate('', (x1, y_dim), (x2, y_dim), arrowprops=dict(arrowstyle='<->', lw=1, color=BLUE))
    ax.text((x1+x2)/2, y_dim + .055, text, ha='center', va='bottom', fontsize=9, color=NAVY,
            bbox=dict(facecolor='white', edgecolor='none', pad=1))


def dim_v(ax, y1, y2, x_ref, x_dim, text):
    for y in (y1, y2):
        ax.plot([x_ref, x_dim + (0.05 if x_dim > x_ref else -0.05)], [y, y], color=GRAY, lw=.75)
    ax.annotate('', (x_dim, y1), (x_dim, y2), arrowprops=dict(arrowstyle='<->', lw=1, color=BLUE))
    ax.text(x_dim-.05, (y1+y2)/2, text, ha='right', va='center', fontsize=9, color=NAVY,
            rotation=90, bbox=dict(facecolor='white', edgecolor='none', pad=1))


def plan_view(L, B, cx, cy):
    fig, ax = plt.subplots(figsize=(9, 7), facecolor='white')
    ax.add_patch(Rectangle((-L/2, -B/2), L, B, facecolor=PALE, edgecolor=NAVY, lw=2.4))
    ax.add_patch(Rectangle((-cx/2, -cy/2), cx, cy, facecolor='#8ca9bc', edgecolor=NAVY, lw=2))
    ax.plot([-L*.68, L*.68], [0, 0], ls=(0, (8, 3, 2, 3)), color=BLUE, lw=1)
    ax.plot([0, 0], [-B*.68, B*.68], ls=(0, (8, 3, 2, 3)), color=BLUE, lw=1)
    ax.text(0, 0, 'C1', ha='center', va='center', color='white', fontsize=11, weight='bold')
    dim_h(ax, -L/2, L/2, -B/2, -B/2-.42, f'{L*1000:.0f} mm')
    dim_v(ax, -B/2, B/2, -L/2, -L/2-.46, f'{B*1000:.0f} mm')
    dim_h(ax, -cx/2, cx/2, cy/2, cy/2+.27, f'{cx*1000:.0f} mm')
    dim_v(ax, -cy/2, cy/2, cx/2, cx/2+.33, f'{cy*1000:.0f} mm')
    ax.text(L/2, B/2+.22, 'FOOTING OUTLINE', ha='right', fontsize=8, color=GRAY)
    ax.set_title('PLAN VIEW | ISOLATED FOOTING', loc='left', color=NAVY, weight='bold', fontsize=14, pad=16)
    clean_axis(ax, (-L/2-.85, L/2+.85), (-B/2-.85, B/2+.7))
    fig.tight_layout(pad=2)
    return fig


def section_view(L, B, cx, cy, t, h):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    ax.add_patch(Rectangle((-L/2, -t), L, t, facecolor='#d5e2e8', edgecolor=NAVY, lw=2, hatch='///'))
    ax.add_patch(Rectangle((-cx/2, 0), cx, h, facecolor='#93aebd', edgecolor=NAVY, lw=2))
    ax.plot([-L*.75, L*.75], [0, 0], color=GRAY, lw=1, ls='--')
    ax.annotate('TOP OF FOOTING', xy=(L/2, 0), xytext=(L/2+.25, .18), fontsize=8,
                arrowprops=dict(arrowstyle='-', color=GRAY), color=GRAY)
    ax.text(-L*.73, .12, 'REFERENCE LEVEL', fontsize=8, color=GRAY)
    dim_h(ax, -L/2, L/2, -t, -t-.36, f'{L*1000:.0f} mm')
    dim_h(ax, -cx/2, cx/2, h, h+.25, f'{cx*1000:.0f} mm')
    dim_v(ax, -t, 0, L/2, L/2+.44, f'{t*1000:.0f} mm')
    dim_v(ax, 0, h, cx/2, L/2+.78, f'{h*1000:.0f} mm')
    ax.text(0, -t/2, 'CONCRETE FOOTING', ha='center', va='center', fontsize=9, color=NAVY,
            bbox=dict(facecolor='white', alpha=.8, edgecolor='none', pad=2))
    ax.text(0, h*.53, 'COLUMN', ha='center', va='center', fontsize=9, color=NAVY, rotation=90)
    ax.set_title('SECTION A–A | SCHEMATIC', loc='left', color=NAVY, weight='bold', fontsize=14, pad=16)
    clean_axis(ax, (-L/2-.7, L/2+1.2), (-t-.65, h+.55))
    fig.tight_layout(pad=2)
    return fig


def cuboid(ax, xmin, xmax, ymin, ymax, zmin, zmax, color):
    p = [
        [(xmin,ymin,zmin),(xmax,ymin,zmin),(xmax,ymax,zmin),(xmin,ymax,zmin)],
        [(xmin,ymin,zmax),(xmax,ymin,zmax),(xmax,ymax,zmax),(xmin,ymax,zmax)],
        [(xmin,ymin,zmin),(xmax,ymin,zmin),(xmax,ymin,zmax),(xmin,ymin,zmax)],
        [(xmax,ymin,zmin),(xmax,ymax,zmin),(xmax,ymax,zmax),(xmax,ymin,zmax)],
        [(xmax,ymax,zmin),(xmin,ymax,zmin),(xmin,ymax,zmax),(xmax,ymax,zmax)],
        [(xmin,ymax,zmin),(xmin,ymin,zmin),(xmin,ymin,zmax),(xmin,ymax,zmax)],
    ]
    ax.add_collection3d(Poly3DCollection(p, facecolors=color, edgecolors=NAVY, linewidths=.9, alpha=.98))


def model_view(L, B, cx, cy, t, h):
    fig = plt.figure(figsize=(9, 7), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    cuboid(ax, -L/2, L/2, -B/2, B/2, 0, t, '#b9cdd8')
    cuboid(ax, -cx/2, cx/2, -cy/2, cy/2, t, t+h, '#759bad')
    ax.set_xlim(-L*.7, L*.7)
    ax.set_ylim(-B*.7, B*.7)
    ax.set_zlim(0, max(t+h, L*.65))
    ax.set_box_aspect((L, B, max(t+h, L*.65)), zoom=.83)
    ax.view_init(elev=24, azim=-55)
    ax.set_axis_off()
    ax.set_title('3D ISOMETRIC | GEOMETRY MODEL', loc='left', color=NAVY, weight='bold', fontsize=14, pad=16)
    fig.tight_layout(pad=1)
    return fig



def bar_layout(L, B, cx, cy, t, h, cover, bar_d, spacing, col_d, tie_spacing):
    """Conceptual bar centreline geometry and quantities, all in metres."""
    x_min, x_max = -L/2 + cover + bar_d/2, L/2 - cover - bar_d/2
    y_min, y_max = -B/2 + cover + bar_d/2, B/2 - cover - bar_d/2
    z1, z2 = cover + bar_d/2, cover + 1.5*bar_d
    footing_ok = (x_max > x_min and y_max > y_min and z2 + bar_d/2 <= t - cover)
    nx = max(2, int(np.ceil((x_max-x_min)/spacing))+1) if footing_ok else 0
    ny = max(2, int(np.ceil((y_max-y_min)/spacing))+1) if footing_ok else 0
    inset = max(.035, col_d/2 + .025)
    x0,x1 = -cx/2+inset, cx/2-inset
    y0,y1 = -cy/2+inset, cy/2-inset
    column_ok = x1 > x0 and y1 > y0 and h > .10
    nt = max(2,int(np.ceil((h-.10)/tie_spacing))+1) if column_ok else 0
    return dict(x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,z1=z1,z2=z2,
                nx=nx,ny=ny,x0=x0,x1=x1,y0=y0,y1=y1,nt=nt,
                footing_ok=footing_ok,column_ok=column_ok)


def reinforcement_schedule(L, B, cx, cy, t, h, cover, bar_d, spacing, col_d, tie_spacing):
    """Illustrative straight-line lengths only; excludes hooks, bends and anchorage."""
    d = bar_layout(L,B,cx,cy,t,h,cover,bar_d,spacing,col_d,tie_spacing)
    rows = []
    if d['footing_ok']:
        rows.extend([
            dict(Member='Footing X bars', Diameter_mm=round(bar_d*1000), Count=d['ny'],
                 Straight_length_mm=round((d['x_max']-d['x_min'])*1000),
                 Total_length_m=round(d['ny']*(d['x_max']-d['x_min']),2)),
            dict(Member='Footing Y bars', Diameter_mm=round(bar_d*1000), Count=d['nx'],
                 Straight_length_mm=round((d['y_max']-d['y_min'])*1000),
                 Total_length_m=round(d['nx']*(d['y_max']-d['y_min']),2)),
        ])
    if d['column_ok']:
        vertical_length = h-.05
        perimeter = 2*((d['x1']-d['x0'])+(d['y1']-d['y0']))
        rows.extend([
            dict(Member='Column vertical bars',Diameter_mm=round(col_d*1000),Count=8,
                 Straight_length_mm=round(vertical_length*1000),
                 Total_length_m=round(8*vertical_length,2)),
            dict(Member='Column ties',Diameter_mm='Not specified',Count=d['nt'],
                 Straight_length_mm=round(perimeter*1000),
                 Total_length_m=round(d['nt']*perimeter,2)),
        ])
    return rows, d


def interactive_rebar_model(L, B, cx, cy, t, h, cover, bar_d, spacing, col_d, tie_spacing,
                             show_concrete=True, show_footing=True, show_column=True,
                             transparency=.20, camera_name='Isometric', exploded=False,
                             show_labels=True):
    """Interactive conceptual model; not a structural reinforcement design."""
    fig = go.Figure()
    d = bar_layout(L,B,cx,cy,t,h,cover,bar_d,spacing,col_d,tie_spacing)
    # In exploded mode only the concrete column is displaced upward for visibility.
    lift = .30 * max(L,B) if exploded else 0.0

    def box_mesh(x0,x1,y0,y1,z0,z1,color,opacity,name):
        vertices = np.array([
            [x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
            [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
        faces = [(0,1,2),(0,2,3),(4,6,5),(4,7,6),
                 (0,4,5),(0,5,1),(1,5,6),(1,6,2),
                 (2,6,7),(2,7,3),(3,7,4),(3,4,0)]
        fig.add_trace(go.Mesh3d(x=vertices[:,0],y=vertices[:,1],z=vertices[:,2],
            i=[a for a,b,c in faces],j=[b for a,b,c in faces],k=[c for a,b,c in faces],
            color=color,opacity=opacity,flatshading=True,name=name,
            hovertemplate=name+'<extra></extra>',showscale=False,
            lighting=dict(ambient=.62,diffuse=.8,specular=.20,roughness=.75)))
        # Light technical outlines, one trace per box.
        edges=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
               (0,4),(1,5),(2,6),(3,7)]
        ex,ey,ez=[],[],[]
        for a,b in edges:
            ex.extend([vertices[a,0],vertices[b,0],None])
            ey.extend([vertices[a,1],vertices[b,1],None])
            ez.extend([vertices[a,2],vertices[b,2],None])
        fig.add_trace(go.Scatter3d(x=ex,y=ey,z=ez,mode='lines',
            line=dict(color='#526b80',width=3),showlegend=False,hoverinfo='skip'))

    def steel_lines(segments,name,color,width=6):
        if not segments:
            return
        xs,ys,zs=[],[],[]
        for x,y,z in segments:
            xs.extend(list(x)+[None]); ys.extend(list(y)+[None]); zs.extend(list(z)+[None])
        fig.add_trace(go.Scatter3d(x=xs,y=ys,z=zs,mode='lines',name=name,
            line=dict(color=color,width=width),hovertemplate=name+'<extra></extra>'))

    if show_concrete:
        box_mesh(-L/2,L/2,-B/2,B/2,0,t,'#b6cbd8',transparency,'Footing concrete')
        box_mesh(-cx/2,cx/2,-cy/2,cy/2,t+lift,t+h+lift,
                 '#7d9bb0',transparency,'Column concrete')

    if show_footing and d['footing_ok']:
        xbars=[([d['x_min'],d['x_max']],[y,y],[d['z1'],d['z1']])
               for y in np.linspace(d['y_min'],d['y_max'],d['ny'])]
        ybars=[([x,x],[d['y_min'],d['y_max']],[d['z2'],d['z2']])
               for x in np.linspace(d['x_min'],d['x_max'],d['nx'])]
        steel_lines(xbars,'Footing steel | X direction','#b66c35',7)
        steel_lines(ybars,'Footing steel | Y direction','#e1a454',7)

    if show_column and d['column_ok']:
        x0,x1,y0,y1=d['x0'],d['x1'],d['y0'],d['y1']
        positions=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),
                   ((x0+x1)/2,y0),(x1,(y0+y1)/2),
                   ((x0+x1)/2,y1),(x0,(y0+y1)/2)]
        vertical=[([x,x],[y,y],[t+.02,t+h-.03]) for x,y in positions]
        ties=[([x0,x1,x1,x0,x0],[y0,y0,y1,y1,y0],[z]*5)
              for z in np.linspace(t+.05,t+h-.05,d['nt'])]
        steel_lines(vertical,'Column vertical bars | 8 conceptual','#98522f',8)
        steel_lines(ties,'Column ties | conceptual','#e6aa50',5)

    if show_labels:
        fig.add_trace(go.Scatter3d(x=[L*.54,0],y=[-B*.55,0],z=[0,t+h+lift+.10],
            mode='text',text=[f'Footing {L*1000:.0f} × {B*1000:.0f} × {t*1000:.0f} mm',
                              f'Column {cx*1000:.0f} × {cy*1000:.0f} mm'],
            textfont=dict(size=11,color='#183550'),showlegend=False,hoverinfo='skip'))

    cameras={
        'Isometric':dict(eye=dict(x=1.7,y=-1.8,z=1.25)),
        'Top':dict(eye=dict(x=0,y=0,z=2.4),up=dict(x=0,y=1,z=0)),
        'Front':dict(eye=dict(x=0,y=-2.5,z=.55)),
        'Side':dict(eye=dict(x=2.5,y=0,z=.55)),
    }
    fig.update_layout(
        title=dict(text='FOUNDAX AI | 3D REINFORCEMENT STUDIO',x=.025,
                   font=dict(size=17,color='#19334d')),
        paper_bgcolor='white',margin=dict(l=0,r=0,b=0,t=65),height=700,
        scene=dict(xaxis=dict(title='X (m)',gridcolor='#d9e4ec',backgroundcolor='#f6f9fc'),
                   yaxis=dict(title='Y (m)',gridcolor='#d9e4ec',backgroundcolor='#f6f9fc'),
                   zaxis=dict(title='Z (m)',gridcolor='#d9e4ec',backgroundcolor='#f6f9fc'),
                   aspectmode='data',camera=cameras[camera_name]),
        legend=dict(orientation='h',y=-.08,x=0,font=dict(size=11)),
        uirevision=camera_name,
    )
    return fig


def as_png(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=210, facecolor='white', bbox_inches='tight')
    return buf.getvalue()


def make_sheet(figures, details):
    """Three A3 landscape sheets, one view per sheet, each with a title block."""
    buf = BytesIO()
    with PdfPages(buf) as pdf:
        for i, (name, view) in enumerate(figures, start=1):
            sheet = plt.figure(figsize=(16.54, 11.69), facecolor='white')
            sheet.text(.055, .945, 'FOUNDAX AI', fontsize=24, weight='bold', color=NAVY)
            sheet.text(.055, .915, 'PRELIMINARY FOUNDATION GEOMETRY | ENGINEERING DRAWING', fontsize=11, color=GRAY)
            sheet.text(.94, .944, f'SHEET {i} / 3', fontsize=11, ha='right', color=NAVY)
            image = as_png(view)
            import matplotlib.image as mpimg
            img = mpimg.imread(BytesIO(image), format='png')
            ax = sheet.add_axes((.065, .18, .87, .70))
            ax.imshow(img)
            ax.axis('off')
            sheet.add_artist(plt.Line2D([.05, .95], [.155, .155], transform=sheet.transFigure, color=NAVY, lw=1.5))
            sheet.text(.055, .125, f'DRAWING: {name}', fontsize=11, weight='bold', color=NAVY)
            sheet.text(.055, .091, f'FOOTING: {details["L"]*1000:.0f} × {details["B"]*1000:.0f} × {details["t"]*1000:.0f} mm', fontsize=9, color=INK)
            sheet.text(.055, .065, f'COLUMN: {details["cx"]*1000:.0f} × {details["cy"]*1000:.0f} mm', fontsize=9, color=INK)
            sheet.text(.49, .125, f'LOAD: {details["P"]:.1f} kN', fontsize=9, color=INK)
            sheet.text(.49, .095, f'SBC: {details["sbc"]:.1f} kN/m²', fontsize=9, color=INK)
            sheet.text(.49, .065, f'BEARING PRESSURE: {details["q"]:.1f} kN/m²', fontsize=9, color=INK)
            sheet.text(.94, .125, f'DATE: {date.today():%d-%m-%Y}', fontsize=9, ha='right', color=INK)
            sheet.text(.94, .095, f'DWG NO: FDX-{i:03d}', fontsize=9, ha='right', color=INK)
            sheet.text(.94, .065, 'UNITS: mm | NOT TO SCALE', fontsize=9, ha='right', color=INK)
            sheet.text(.5, .025, 'EDUCATIONAL PRELIMINARY DRAWING — NOT FOR CONSTRUCTION',
                       ha='center', fontsize=10, color='#a63b35', weight='bold')
            pdf.savefig(sheet, dpi=170)
            plt.close(sheet)
    return buf.getvalue()


st.title('FOUNDAX AI | Professional Footing Drawing Studio')
st.caption('Dimensioned 2D plan • Section A–A • 3D isometric • A3 PDF drawing sheets')
st.warning('Preliminary schematic only. Structural capacity, settlement, reinforcement and code compliance are not verified. Not for construction.')

with st.sidebar:
    st.subheader('Drawing Inputs')
    P = st.number_input('Column service load (kN)', min_value=1.0, value=1000.0, step=50.0)
    sbc = st.number_input('Allowable soil bearing pressure (kN/m²)', min_value=1.0, value=200.0, step=10.0)
    cx_mm = st.number_input('Column size X (mm)', min_value=100, value=400, step=50)
    cy_mm = st.number_input('Column size Y (mm)', min_value=100, value=500, step=50)
    t_mm = st.number_input('Footing thickness (mm)', min_value=150, value=450, step=25)
    h_mm = st.number_input('Visible column height (mm)', min_value=200, value=1000, step=100)
    allowance = st.slider('Preliminary area allowance (%)', min_value=0, max_value=30, value=10, step=5)
    shape = st.selectbox('Footing plan shape', ['Square', 'Rectangular (column aspect ratio)'])

cx, cy, t, h = cx_mm/1000, cy_mm/1000, t_mm/1000, h_mm/1000
required = P/sbc * (1 + allowance/100)
if shape == 'Square':
    L = B = ceil_to(max(sqrt(required), cx, cy), .1)
else:
    ratio = max(cx/cy, .25)
    L = ceil_to(max(sqrt(required*ratio), cx), .1)
    B = ceil_to(max(required/L, cy), .1)
    while L*B + 1e-9 < required:
        B = round(B+.1, 5)

provided = L*B
q = P/provided
c1, c2, c3, c4 = st.columns(4)
c1.metric('Footing Length', f'{L:.2f} m')
c2.metric('Footing Width', f'{B:.2f} m')
c3.metric('Provided Area', f'{provided:.2f} m²')
c4.metric('Service Pressure', f'{q:.2f} kN/m²')
st.caption(f'Preliminary sizing: A = (P / SBC) × (1 + allowance) = ({P:.1f} / {sbc:.1f}) × {1+allowance/100:.2f} = {required:.2f} m². Rounded dimensions: {L:.2f} × {B:.2f} m. Column assumed centred.')

plan = plan_view(L, B, cx, cy)
section = section_view(L, B, cx, cy, t, h)
model = model_view(L, B, cx, cy, t, h)
figures = [('PLAN VIEW', plan), ('SECTION A-A', section), ('3D ISOMETRIC', model)]
tabs = st.tabs(['2D Plan', 'Section A–A', 'Interactive 3D Reinforcement'])
with tabs[0]:
    st.pyplot(plan, clear_figure=False, width='stretch')
    st.download_button('Download PLAN VIEW PNG', as_png(plan),
                       file_name='FOUNDAX_AI_plan.png', mime='image/png', key='dl_plan')
with tabs[1]:
    st.pyplot(section, clear_figure=False, width='stretch')
    st.download_button('Download SECTION A-A PNG', as_png(section),
                       file_name='FOUNDAX_AI_section.png', mime='image/png', key='dl_section')
with tabs[2]:
    st.caption('Mouse se rotate aur zoom karo. Camera preset select karke specific view dekho.')
    control_a, control_b, control_c = st.columns(3)
    with control_a:
        cover_mm = st.number_input('Illustrative concrete cover (mm)',25,100,50,5)
        bar_mm = st.selectbox('Footing bar diameter (mm)',[10,12,16,20],index=1)
        spacing_mm = st.number_input('Footing bar spacing (mm)',75,300,150,25)
    with control_b:
        col_bar_mm = st.selectbox('Column bar diameter (mm)',[12,16,20,25],index=1)
        tie_spacing_mm = st.number_input('Column tie spacing (mm)',75,300,150,25)
        camera_name = st.selectbox('Camera view',['Isometric','Top','Front','Side'])
    with control_c:
        show_concrete = st.checkbox('Show concrete',True)
        show_footing = st.checkbox('Show footing steel',True)
        show_column = st.checkbox('Show column steel and ties',True)
        exploded = st.checkbox('Exploded concrete column view',False)
        show_labels = st.checkbox('Show dimension labels',True)
        transparency = st.slider('Concrete opacity (%)',5,90,22,5)/100

    schedule, geometry = reinforcement_schedule(
        L,B,cx,cy,t,h,cover_mm/1000,bar_mm/1000,spacing_mm/1000,
        col_bar_mm/1000,tie_spacing_mm/1000)
    if not geometry['footing_ok']:
        st.warning('Footing thickness / cover / bar diameter combination me bottom mesh fit nahi ho raha.')
    if not geometry['column_ok']:
        st.warning('Column dimensions ke andar illustrative 8-bar arrangement fit nahi ho raha.')

    fig3d = interactive_rebar_model(
        L,B,cx,cy,t,h,cover_mm/1000,bar_mm/1000,spacing_mm/1000,
        col_bar_mm/1000,tie_spacing_mm/1000,
        show_concrete=show_concrete,show_footing=show_footing,
        show_column=show_column,transparency=transparency,
        camera_name=camera_name,exploded=exploded,show_labels=show_labels)
    st.plotly_chart(fig3d,width='stretch',config={'displaylogo':False,
                    'toImageButtonOptions':{'format':'png','filename':'FOUNDAX_AI_3D_Reinforcement',
                                             'height':1100,'width':1500,'scale':2}})
    if exploded:
        st.info('Exploded view me sirf concrete column upar shift hota hai. Steel apni original position par rehta hai.')

    st.subheader('Illustrative Reinforcement Schedule')
    if schedule:
        st.dataframe(schedule,width='stretch',hide_index=True)
        output=StringIO()
        writer=csv.DictWriter(output,fieldnames=list(schedule[0].keys()))
        writer.writeheader()
        writer.writerows(schedule)
        st.download_button('Download Schedule CSV',output.getvalue().encode('utf-8'),
                           'FOUNDAX_AI_Illustrative_Rebar_Schedule.csv','text/csv')
    else:
        st.warning('Current dimensions par illustrative reinforcement schedule available nahi hai.')

    st.download_button('Download Interactive 3D HTML',
        fig3d.to_html(full_html=True,include_plotlyjs=True).encode('utf-8'),
        file_name='FOUNDAX_AI_Interactive_3D_Reinforcement.html',mime='text/html')
    st.warning('CONCEPTUAL REINFORCEMENT — NOT FOR CONSTRUCTION. '
               'Schedule me straight lengths hain; hooks, anchorage, lap, bends, '
               'structural capacity aur code checks included nahi hain. '
               'Column ties ka diameter input nahi liya gaya hai.')
    st.caption('A3 PDF me existing static 3D geometry preserved hai. '
               'Interactive reinforcement model ko HTML me download kar sakte ho.')

pdf = make_sheet(figures, dict(L=L, B=B, cx=cx, cy=cy, t=t, P=P, sbc=sbc, q=q))
st.download_button('Download Professional A3 PDF Drawing Set', pdf,
                   file_name='FOUNDAX_AI_Preliminary_Footing_Drawings_A3.pdf', mime='application/pdf', type='primary')
st.info('The area allowance is illustrative, not a verified self-weight or settlement calculation. Reinforcement shown in the interactive 3D view is conceptual only; no structural reinforcement design has been performed.')
for _, fig in figures:
    plt.close(fig)


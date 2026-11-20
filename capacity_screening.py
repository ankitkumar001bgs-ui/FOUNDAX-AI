"""Independent educational screening functions; not a code-certified design engine."""
import math

def calculate(B,L,cx,cy,D,d,P,qu,fck,fy,bar_dia,provided_spacing,tau_one,tau_punch,xu_limit):
    vals=[B,L,cx,cy,D,d,P,qu,fck,fy,bar_dia,provided_spacing,tau_one,tau_punch,xu_limit]
    if not all(math.isfinite(v) and v>0 for v in vals):raise ValueError("All inputs must be finite and positive")
    if cx>=B or cy>=L or d>=D or not 0<xu_limit<1:raise ValueError("Invalid column/footing geometry, depth or x_u limit")
    dm=d/1000; ax=(B-cx)/2; ay=(L-cy)/2
    if cx+dm>=B or cy+dm>=L:raise ValueError("Interior punching perimeter outside footing; this simplified model is inapplicable")
    if abs(qu-P/(B*L))/max(qu,P/(B*L))>0.05:raise ValueError("Factored P and q_u inconsistent by over 5%; verify equilibrium")
    mx=qu*ax*ax/2; my=qu*ay*ay/2
    vx=qu*max(ax-dm,0);vy=qu*max(ay-dm,0)
    vp=qu*(B*L-(cx+dm)*(cy+dm))
    b=1000.0
    # mu = 0.87 fy Ast (d - 0.42 xu); xu = 0.87 fy Ast/(0.36 fck b)
    def flexure(moment):
        target=moment*1e6
        a=0.87*fy*d
        coeff=(0.87*fy)*(0.42*0.87*fy/(0.36*fck*b))
        discriminant=a*a-4*coeff*target
        if discriminant<0: return None,None,None
        ast=(a-math.sqrt(discriminant))/(2*coeff) if coeff else target/a
        xu=0.87*fy*ast/(0.36*fck*b)
        return ast,xu,xu/d
    ax_req,xux,rx=flexure(mx);ay_req,xuy,ry=flexure(my)
    area_bar=math.pi*bar_dia**2/4
    provided=area_bar*1000/provided_spacing
    def capacity(ast):
        xu=0.87*fy*ast/(0.36*fck*b)
        if xu/d>xu_limit:return None
        return 0.87*fy*ast*(d-0.42*xu)/1e6
    mu_prov=capacity(provided)
    tau_vx=vx*1000/(b*d);tau_vy=vy*1000/(b*d)
    perimeter=2*(cx+cy+2*dm)*1000
    tau_vp=vp*1000/(perimeter*d)
    return {'Mu B (kN.m/m)':mx,'Mu L (kN.m/m)':my,'Ast req B (mm²/m)':ax_req,'Ast req L (mm²/m)':ay_req,
      'Ast provided (mm²/m)':provided,'xu/d B':rx,'xu/d L':ry,'Mu provided (kN.m/m)':mu_prov,
      'One-way tau B (N/mm²)':tau_vx,'One-way tau L (N/mm²)':tau_vy,'Punching tau (N/mm²)':tau_vp,
      'Flexure screening':('REVIEW' if ax_req is None or ay_req is None or rx>xu_limit or ry>xu_limit or mu_prov is None or mu_prov<max(mx,my) else 'WITHIN INPUT LIMITS'),
      'One-way screening':('WITHIN INPUT LIMITS' if max(tau_vx,tau_vy)<=tau_one else 'REVIEW'),
      'Punching screening':('WITHIN INPUT LIMITS' if tau_vp<=tau_punch else 'REVIEW')}

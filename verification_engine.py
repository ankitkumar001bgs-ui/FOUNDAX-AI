"""Transparent preliminary bearing-pressure benchmark; NOT a code-compliant footing design."""
import math

def bearing_check(load_kn, length_m, width_m, sbc_kn_m2, mx_knm=0.0, my_knm=0.0, allowance_pct=0.0):
    vals=(load_kn,length_m,width_m,sbc_kn_m2,mx_knm,my_knm,allowance_pct)
    if not all(math.isfinite(float(v)) for v in vals):
        raise ValueError('All inputs must be finite numbers.')
    if min(load_kn,length_m,width_m,sbc_kn_m2)<=0 or allowance_pct<0:
        raise ValueError('Load, dimensions and SBC must be positive; allowance cannot be negative.')
    gross_load=load_kn*(1+allowance_pct/100)
    area=length_m*width_m
    qavg=gross_load/area
    ex=my_knm/gross_load
    ey=mx_knm/gross_load
    # Full-contact, rigid rectangular base; superposition of linear pressure distribution.
    delta_x=6*abs(my_knm)/(width_m*length_m**2)
    delta_y=6*abs(mx_knm)/(length_m*width_m**2)
    qmax=qavg+delta_x+delta_y
    qmin=qavg-delta_x-delta_y
    kern=abs(ex)/length_m+abs(ey)/width_m<=1/6+1e-10
    return dict(area_m2=area,gross_load_kn=gross_load,required_area_m2=gross_load/sbc_kn_m2,
                average_pressure_kn_m2=qavg,maximum_pressure_kn_m2=qmax,
                minimum_pressure_kn_m2=qmin,eccentricity_x_m=ex,eccentricity_y_m=ey,
                full_contact=kern,bearing_within_sbc=(kern and qmax<=sbc_kn_m2+1e-10),
                preliminary_area_sufficient=area>=gross_load/sbc_kn_m2)

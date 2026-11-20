"""Auditable educational comparison of documented footing geometry; not a structural design engine."""
from math import ceil, isfinite, sqrt

REQUIRED = ('Column ID', 'Service Load (kN)', 'Drawing Width (m)', 'Drawing Length (m)', 'Drawing Thickness (m)')

def positive(value, label):
    x = float(value)
    if not isfinite(x) or x <= 0:
        raise ValueError(f'{label} must be positive and finite')
    return x

def compare_footing(row, sbc, allowance_pct, increment, assumed_thickness, depth, concrete_rate, excavation_rate):
    label = str(row['Column ID']).strip()
    if not label or label.lower() == 'nan':
        raise ValueError('Column ID is required')
    load = positive(row['Service Load (kN)'], 'Service Load')
    width = positive(row['Drawing Width (m)'], 'Drawing Width')
    length = positive(row['Drawing Length (m)'], 'Drawing Length')
    thickness = positive(row['Drawing Thickness (m)'], 'Drawing Thickness')
    sbc = positive(sbc, 'SBC')
    increment = positive(increment, 'Rounding increment')
    assumed_thickness = positive(assumed_thickness, 'Assumed comparison thickness')
    depth = positive(depth, 'Excavation depth')
    if not (0 <= allowance_pct <= 30):
        raise ValueError('Allowance must be between 0 and 30 percent')
    if concrete_rate < 0 or excavation_rate < 0:
        raise ValueError('Unit rates must not be negative')
    adjusted_load = load * (1 + allowance_pct / 100)
    required_area = adjusted_load / sbc
    side = round(ceil(sqrt(required_area) / increment - 1e-10) * increment, 4)
    drawing_area = width * length
    drawing_pressure = adjusted_load / drawing_area
    comparison_area = side * side
    comparison_pressure = adjusted_load / comparison_area
    drawing_concrete = drawing_area * thickness
    comparison_concrete = comparison_area * assumed_thickness
    drawing_excavation = drawing_area * depth
    comparison_excavation = comparison_area * depth
    drawing_cost = drawing_concrete * concrete_rate + drawing_excavation * excavation_rate
    comparison_cost = comparison_concrete * concrete_rate + comparison_excavation * excavation_rate
    difference = drawing_cost - comparison_cost
    return {
        'Column ID': label,
        'Service Load (kN)': round(load, 2),
        'Drawing Area (m²)': round(drawing_area, 3),
        'Drawing Pressure (kN/m²)': round(drawing_pressure, 2),
        'Drawing Bearing Screening': 'ABOVE ENTERED SBC' if drawing_pressure > sbc + 1e-8 else 'WITHIN ENTERED SBC (AREA ONLY)',
        'Comparison Square Side (m)': side,
        'Comparison Area (m²)': round(comparison_area, 3),
        'Comparison Pressure (kN/m²)': round(comparison_pressure, 2),
        'Drawing Concrete (m³)': round(drawing_concrete, 3),
        'Comparison Concrete (m³)': round(comparison_concrete, 3),
        'Drawing Excavation (m³)': round(drawing_excavation, 3),
        'Comparison Excavation (m³)': round(comparison_excavation, 3),
        'Drawing Partial Cost (INR)': round(drawing_cost, 2),
        'Comparison Partial Cost (INR)': round(comparison_cost, 2),
        'Partial Cost Difference (INR)': round(difference, 2),
        'Comparison Status': 'NOT STRUCTURALLY VERIFIED',
    }

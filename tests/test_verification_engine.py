import math
import pytest
from verification_engine import bearing_check

def test_concentric_bearing():
    r=bearing_check(800,2,2,200)
    assert r['area_m2']==4
    assert r['maximum_pressure_kn_m2']==200
    assert r['minimum_pressure_kn_m2']==200
    assert r['bearing_within_sbc']

def test_uniaxial_eccentricity():
    r=bearing_check(600,3,2,200,my_knm=60)
    assert math.isclose(r['maximum_pressure_kn_m2'],120)
    assert math.isclose(r['minimum_pressure_kn_m2'],80)
    assert r['full_contact']

def test_no_contact_warning():
    r=bearing_check(100,2,2,200,my_knm=50)
    assert not r['full_contact']
    assert not r['bearing_within_sbc']

def test_bad_inputs():
    with pytest.raises(ValueError):
        bearing_check(800,0,2,200)

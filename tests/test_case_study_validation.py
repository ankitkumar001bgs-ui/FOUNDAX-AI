import unittest
from case_study_validation_engine import compare_footing

class TestCaseStudy(unittest.TestCase):
    def setUp(self):
        self.row={'Column ID':'C1','Service Load (kN)':800,'Drawing Width (m)':2,'Drawing Length (m)':2,'Drawing Thickness (m)':0.5}
    def test_area_and_pressure(self):
        r=compare_footing(self.row,200,0,0.1,0.5,1.5,7000,400)
        self.assertAlmostEqual(r['Comparison Square Side (m)'],2)
        self.assertAlmostEqual(r['Drawing Pressure (kN/m²)'],200)
        self.assertAlmostEqual(r['Partial Cost Difference (INR)'],0)
    def test_high_pressure_warning(self):
        r=compare_footing(self.row,150,0,0.1,0.5,1.5,7000,400)
        self.assertEqual(r['Drawing Bearing Screening'],'ABOVE ENTERED SBC')
    def test_invalid_load(self):
        self.row['Service Load (kN)']=-5
        with self.assertRaises(ValueError):
            compare_footing(self.row,200,0,0.1,0.5,1.5,7000,400)

if __name__=='__main__': unittest.main()

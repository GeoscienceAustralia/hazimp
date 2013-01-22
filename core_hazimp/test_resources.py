# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases
# pylint: disable=E1123
# pylint says;  Passing unexpected keyword argument 'delete' in function call
# I need to pass it though.
# pylint: disable=R0801



"""
Test the data in resources.  Can it be loaded?
"""

import unittest
#import tempfile
import os

#import numpy
#from scipy import asarray, allclose

from core_hazimp.misc import RESOURCE_DIR
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file

class TestResources(unittest.TestCase): 
    """
    Test the data in resources.
    """
    def test_domestic_wind_vul_curves(self):
        vuln_sets = vuln_sets_from_xml_file(os.path.join(RESOURCE_DIR, 
                                             'domestic_wind_vul_curves.xml'))
        self.assertEqual(vuln_sets["domestic_wind_2012"].intensity_measure_type,
                         "0.2s gust at 10m height m/s")
        
        # Check the first loss value of the last model
        vul_funct = vuln_sets["domestic_wind_2012"].vulnerability_functions[
            'dw306']
        self.assertAlmostEqual(vul_funct.mean_loss[0], 0.0)
    
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestResources,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

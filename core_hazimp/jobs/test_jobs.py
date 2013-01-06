# -*- coding: utf-8 -*-
# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the calcs module.
"""

import unittest
import tempfile
import os
from scipy import allclose, asarray

from core_hazimp.jobs.jobs import JOBS
from core_hazimp.jobs.test_vulnerability_model import build_example
from core_hazimp.jobs import jobs

class Dummy:
    """
    Dummy class for testing
    """
    def __init__(self):
        # For test_SimpleLinker
        self.vul_function_titles = {}

        # For test_SelectVulnFunction
        self.vulnerability_sets = {}
        self.exposure_att = {}
        

class DummyVulnSet:
    """
    Dummy class of vuln_set for testing.
    """
    def __init__(self, vuln_set):
        # For test_SimpleLinker
        self.vuln_set = vuln_set
        
    def build_realised_vuln_curves(self, vuln_function_ids,
                variability_method):
        """For test_SimpleLinker
        """
        
        return (vuln_function_ids,
                variability_method, 
                self.vuln_set)
                
class TestJobs(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_const_test(self):
        inst = JOBS['const_test']
        context = Dummy
        context.exposure_att = {'a_test':5, 'b_test':20}
        #config = {'eggs':{'c_test':25}}
        test_kwargs = {'c_test':25}
        inst(context, **test_kwargs)
        self.assertEqual(context.exposure_att['c_test'], 25)

        
    def test_load_csv_exposure(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.txt', 
                                        prefix='test_jobs',
                                        delete=False)
        f.write('exposure_lat, exposure_long, Z\n')
        f.write('1., 2., 3.\n')
        f.write('4., 5., 6.\n')
        f.close()
        
        inst = JOBS['load_csv_exposure']
        context = Dummy
        context.exposure_lat = None
        context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'exposure_file':f.name}
        inst(context, **test_kwargs)
        
        self.assertTrue(allclose(context.exposure_lat, asarray([1.0, 4.0])))
        self.assertTrue(allclose(context.exposure_long, asarray([2.0, 5.0])))
        self.assertTrue(allclose(context.exposure_att['Z'], 
                                 asarray([3.0, 6.0])))
        
        os.remove(f.name)

    def test_load_vuln_set(self):
        # Write a file to test
        filename = build_example()
        
        context = Dummy
        context.exposure_lat = None
        context.exposure_long = None
        context.vulnerability_sets = {}
        test_kwargs = {'vulnerability_file':filename}
        inst = JOBS['load_xml_vulnerability']
        inst(context, **test_kwargs)
        page = context.vulnerability_sets['PAGER']
        
        # This is enough of a check
        # Other tests check that it is fully loaded.
        self.assertEqual(page.asset_category, "chickens")
                                 
        os.remove(filename)
        
    def test_SimpleLinker(self):
        context = Dummy()
        test_kwargs = {'vul_functions_in_exposure':{'food':100}}
        inst = JOBS[jobs.SIMPLELINKER]
        inst(context, **test_kwargs)
        actual = test_kwargs['vul_functions_in_exposure']
        self.assertDictEqual(actual, context.vul_function_titles)
        
    def test_SelectVulnFunction(self):
        set1 = 'Contents'
        set2 = 'Buildings'
        column1 = set1
        column2 = set2
        exp1 = ['con1', 'con2']
        exp2 = ['bld1', 'bld2']
        VulnSet1 = DummyVulnSet(set1)
        VulnSet2 = DummyVulnSet(set2)
        context = Dummy()
        context.vulnerability_sets = {set1:VulnSet1, set2:VulnSet2}
        context.vul_function_titles = {set1:column1, set2:column2}
        context.exposure_att[column1] = exp1
        context.exposure_att[column2] = exp2

        variability_method = {set1:'mean1', set2:'mean2'}
        
        test_kwargs = {'variability_method':
                           variability_method}
        inst = JOBS[jobs.SELECTVULNFUNCTION]
        inst(context, **test_kwargs)
        actual = {set1:(exp1, 'mean1', set1), set2:(exp2, 'mean2', set2)}
        self.assertDictEqual(actual, context.exposure_vuln_curves)
        
        
#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestJobs,'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

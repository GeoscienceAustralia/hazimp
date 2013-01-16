# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the workflow module.
"""

import unittest
import tempfile
import os

from scipy import allclose, asarray

from core_hazimp import workflow
from core_hazimp.workflow import ConfigPipeLineBuilder, Context
from core_hazimp.calcs.calcs import CALCS
from core_hazimp.jobs.jobs import JOBS

class TestWorkFlow(unittest.TestCase): 
    """
    Test the workflow module
    """    
    
    def test_ContextAwareBuilder(self):
        a_test = 5
        b_test = 2
        Cab = ConfigPipeLineBuilder()
        calc_list = [CALCS['add_test'], CALCS['multiply_test'], 
                     CALCS['constant_test']]
        context = Context()
        context.exposure_att = {'a_test':a_test, 'b_test':b_test}
        pipeline = Cab.build(calc_list)
        config = {'constant_test':{'constant':5}}
        pipeline.run(context, config)
        self.assertEqual(context.exposure_att['d_test'], 35)
    
    
    def test_Job_ContextAwareBuilder(self):
    
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.txt', 
                                        prefix='test_jobs',
                                        delete=False)
        f.write('exposure_lat, exposure_long, a_test, b_test\n')
        f.write('1., 2., 3., 30.\n')
        f.write('4., 5., 6., 60.\n')
        f.close()
        
        Cab = ConfigPipeLineBuilder()
        calc_list = [JOBS['load_csv_exposure'], CALCS['add_test']]
        context = Context()
        
        pipeline = Cab.build(calc_list)
        config = {'constant_test':{'c_test':[5., 2.]}, 
                  'load_csv_exposure':{'exposure_file':f.name}}
        pipeline.run(context, config)
        
        self.assertTrue(allclose(context.exposure_att['c_test'],
                                 asarray([33., 66.])))
        
        os.remove(f.name)


    def test_Job_title_fix_ContextAwareBuilder(self):
    
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.txt', 
                                        prefix='test_jobs',
                                        delete=False)
        f.write('LAT, LONG, a_test, b_test,BUILDING\n')
        f.write('1., 2., 3., 30.,TAB\n')
        f.write('4., 5., 6., 60.,DSG\n')
        f.close()
        
        Cab = ConfigPipeLineBuilder()
        calc_list = [JOBS['load_csv_exposure'], CALCS['add_test']]
        context = Context()
        
        pipeline = Cab.build(calc_list)
        config = {'constant_test':{'c_test':[5., 2.]}, 
                  'load_csv_exposure':{'exposure_file':f.name,
                                       workflow.EX_LAT:'LAT',
                                       workflow.EX_LONG:'LONG'}}
        pipeline.run(context, config)
        
        self.assertTrue(allclose(context.exposure_att['c_test'],
                                 asarray([33., 66.])))
        self.assertEqual(context.exposure_att['BUILDING'].tolist(),
                                 ['TAB', 'DSG'])
        os.remove(f.name)
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestWorkFlow,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

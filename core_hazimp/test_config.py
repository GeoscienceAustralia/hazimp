# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the config module.
"""

import unittest

from core_hazimp import config
from core_hazimp.calcs import calcs # import CALCS
from core_hazimp.jobs import jobs # import JOBS

class TestConfig(unittest.TestCase): 
    """
    Test the config module
    """    
    
    def test_get_job_or_calc(self):
        # messy test.  Relies on calcs.py and jobs.py
        name = 'add_test'
        job = config.get_job_or_calc(name)
        self.assertIsInstance(job, calcs.AddTest)
        
        name = 'const_test'
        job = config.get_job_or_calc(name)
        self.assertIsInstance(job, jobs.ConstTest)
        

    def test_job_reader(self):
        config_dic = {'version':1, 'jobs':['add_test']}
        actual = config.template_builder(config_dic)
        self.assertListEqual([calcs.CALCS['add_test']], actual)
          
    
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestConfig,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

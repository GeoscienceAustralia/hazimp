# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)

"""
Test the workflow module.
"""

import unittest

from core_hazimp.workflow import ExposureAttsBuilder, Context
from core_hazimp.calcs.calcs import CALCS

class TestWorkFlow(unittest.TestCase): 
    """
    Test the workflow module
    """    
    
    def test_ContextAwareBuilder(self):
        a_test = 5
        b_test = 2
        Cab = ExposureAttsBuilder()
        calc_list = [CALCS['add_test'], CALCS['multiply_test']]
        context = Context()
        context.exposure_att = {'a_test':a_test, 'b_test':b_test}
        pipeline = Cab.build(calc_list)
        pipeline.run(context)
    
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestWorkFlow,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

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

from core_hazimp.calcs.calcs import CALCS


class Dummy:
    """
    Dummy class for testing
    """
    def __init__(self):
        pass
        
        
class TestCalcs(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_AddTest(self):
        inst = CALCS['add_test']
        context = Dummy
        context.exposure_att = {'a_test':5, 'b_test':20}
        inst(context)
        self.assertEqual(context.exposure_att['c_test'], 25)
        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['c_test'])

        
    def test_MultipleValuesTest(self):
        # Not such a good test though
        inst = CALCS['multiple_values_test']
        context = Dummy
        context.exposure_att = {'a_test':5, 'b_test':20}
        inst(context)
        self.assertEqual(context.exposure_att['e_test'], 5)
        self.assertEqual(context.exposure_att['f_test'], 20)
        
        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['e_test', 'f_test'])
        
    def test_ConstantTestTest(self):
        inst = CALCS['constant_test']
        context = Dummy
        context.exposure_att = {'a_test':5, 'b_test':20}
        inst(context, **{'constant':5})
        self.assertEqual(context.exposure_att['g_test'], 5*2)
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestCalcs,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

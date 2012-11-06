# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have Capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)

"""
Test the calcs module.
"""

import unittest

from core_hazimp.calcs.calcs import CALCS


class TestCalcs(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_AddTest(self):
        inst = CALCS["AddTest"]
        self.assertEqual(inst(5, 20), 25)
        self.assertEqual(inst.args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ('c_test'))

        
    def test_MultipleValuesTest(self):
        # Not such a good test though
        inst = CALCS["MultipleValuesTest"]
        self.assertEqual(inst(5, 20), (5, 20))
        self.assertEqual(inst.args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ('e_test', 'f_test'))
        
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestCalcs,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

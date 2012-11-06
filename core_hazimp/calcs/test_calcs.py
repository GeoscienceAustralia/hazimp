
"""
Test the calcs module
"""

import unittest

from calcs import CALCS


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

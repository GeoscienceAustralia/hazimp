import os
import sys
import unittest

from calcs import CALCS


class Test_calcs(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_Add_a_b_test(self):
        inst = CALCS["AddTest"]
        self.assertEqual(inst(5,20), 25)
        self.assertEqual(inst.args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ('c_test'))

        
    def test_Multiple_values_test(self):
        # Not such a good test though
        inst = CALCS["MultipleValuesTest"]
        self.assertEqual(inst(5,20), (5, 20))
        self.assertEqual(inst.args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ('e_test', 'f_test'))
        
#-------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(Test_calcs,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

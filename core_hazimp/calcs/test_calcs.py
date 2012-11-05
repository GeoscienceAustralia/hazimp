import os
import sys
import unittest

from calcs import calulations


class Test_calcs(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_Add_a_b_test(self):
        inst = calulations["Add_a_b_test"]
        self.assertEqual(inst(5,20), 25)
        self.assertEqual(inst.args_in, ['a', 'b'])
        self.assertEqual(inst.args_out, ('c'))

        
    def test_Multiple_values_test(self):
        # Not such a good test though
        inst = calulations["Multiple_values_test"]
        self.assertEqual(inst(5,20), (5, 20))
        self.assertEqual(inst.args_in, ['a', 'b'])
        self.assertEqual(inst.args_out, ('e', 'f'))
        
#-------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(Test_calcs,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

# -*- coding: utf-8 -*-
# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases
# pylint: disable=R0801
#:  Can not seem to locally disable this warning.

"""
Test wind scenarios.
"""

import unittest
                
class TestWind(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_const_test(self):
        pass
  
        
#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestWind,'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

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



class TestIntegration(unittest.TestCase): 
    """
    Test how all of the modules work in a standard workflow.
    """    
    def test_exposure_and_vuln_functions(self):
        # first create the 'official' interface?
        pass
    
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestIntegration,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

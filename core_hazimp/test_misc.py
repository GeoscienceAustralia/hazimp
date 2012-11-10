# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases



"""
Test the misc module.
"""

import unittest

from core_hazimp.misc import csv2dict 


class TestMisc(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_csv2dict(self):
        # Write a file to test
        file_dict = csv2dict('example.csv')
        self.assertEqual(file_dict, {'X':[1.0, 4.0], 
                                     'Y':[2.0, 5.0],
                                     'Z':[3.0, 6.0]})

        
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestMisc,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

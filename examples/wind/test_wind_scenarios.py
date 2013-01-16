# -*- coding: utf-8 -*-

"""
Test wind scenarios.
"""

import unittest
                
from core_hazimp import hazimp

class TestWind(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_const_test(self):
        # First test running an end to end cyclone test based 
        # on a config dictionary, version 1
        filename = None
        config = {'load_csv_exposure':{'exposure_file':filename,
                                       'exposure_latitude':'LAT',
                                       'exposure_longitude':'LONG'}}
        context = hazimp.main(config_dic=)
        
        
  
        
#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestWind,'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

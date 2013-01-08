# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest" 
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases
# pylint: disable=E1123
# pylint says;  Passing unexpected keyword argument 'delete' in function call
# I need to pass it though.



"""
Test the misc module.
"""

import unittest
import tempfile
import os

from scipy import asarray, allclose

from core_hazimp.misc import csv2dict, raster_data_at_points


class TestMisc(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_csv2dict(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.txt', 
                                        prefix='test_misc',
                                        delete=False)
        f.write('X, Y, Z, A\n')
        f.write('1., 2., 3., yeah\n')
        f.write('4., 5., 6.,me \n')
        f.close()
        
        file_dict = csv2dict(f.name)
        
        self.assertEqual(file_dict, {'X':[1.0, 4.0], 
                                     'Y':[2.0, 5.0],
                                     'Z':[3.0, 6.0],
                                     'A':['yeah', 'me']})
        os.remove(f.name)

        
    def test_raster_data_at_points(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.aai', 
                                        prefix='test_misc',
                                        delete=False)
        f.write('ncols 3 \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner +0. \r\n')
        f.write('yllcorner +8. \r\n')
        f.write('cellsize 1 \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('1 2 3 \r\n')
        f.write('4 5 6 ')
        f.close()
        
        lon = asarray([0, 0.9, 1.1])
        lat = asarray([10, 9.1, 8.9])
        a_file = f.name
        data = raster_data_at_points(lon, lat, [a_file])
        
        self.assertTrue(allclose(data, asarray([1., 1., 5.])))
        os.remove(f.name)
      
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestMisc,'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

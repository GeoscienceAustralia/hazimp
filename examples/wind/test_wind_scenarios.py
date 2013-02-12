# -*- coding: utf-8 -*-

"""
Test wind scenarios.
"""

import unittest
import os
import tempfile
import numpy

from scipy import allclose
                
from core_hazimp import hazimp                
from core_hazimp import misc

from core_hazimp.jobs.jobs import LOADRASTER, LOADCSVEXPOSURE, \
    LOADXMLVULNERABILITY, SIMPLELINKER, SELECTVULNFUNCTION, \
    LOOKUP, SAVEEXPOSURE
from core_hazimp.calcs.calcs import STRUCT_LOSS

class TestWind(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_const_test(self):
        # First test running an end to end cyclone test based 
        # on a config dictionary, version 1'
        
        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz', 
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)
        
        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir, 'small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        vul_filename = os.path.join(misc.RESOURCE_DIR, 
                                    'domestic_wind_vul_curves.xml')
        config = {
            'jobs':[LOADCSVEXPOSURE, LOADRASTER, LOADXMLVULNERABILITY,
            SIMPLELINKER, SELECTVULNFUNCTION, LOOKUP, STRUCT_LOSS,
            SAVEEXPOSURE],
            LOADCSVEXPOSURE:{'exposure_file':exp_filename,
                                 'exposure_latitude':'latitude',
                                 'exposure_longitude':'longitude'},
            LOADRASTER:{'file_list':[wind_filename],
                        'attribute_label':'0.2s gust at 10m height m/s'},
            LOADXMLVULNERABILITY:{'vulnerability_file':vul_filename},
            SIMPLELINKER:{'vul_functions_in_exposure':{
                    'domestic_wind_2012':'wind_vulnerability_model'}},
            SELECTVULNFUNCTION:{'variability_method':{
                    'domestic_wind_2012':'mean'}},
            SAVEEXPOSURE:{'file_name':f.name}}
            
        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(context.exposure_att['structural_loss'],
                                 context.exposure_att['calced-loss']))
        
        exp_dict = numpy.load(f.name)
        self.assertTrue(allclose(exp_dict['structural_loss'],
                                 exp_dict['calced-loss']))
        os.remove(f.name)
#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestWind,'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

# -*- coding: utf-8 -*-

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test wind scenarios.
"""
from __future__ import print_function  # can now use print()

import unittest
import os
import tempfile
import numpy

from scipy import allclose

from core_hazimp import misc
from core_hazimp import hazimp
from core_hazimp.jobs.jobs import (LOADRASTER, LOADCSVEXPOSURE,
                                   LOADXMLVULNERABILITY, SIMPLELINKER,
                                   SELECTVULNFUNCTION,
                                   LOOKUP, SAVEALL)
from core_hazimp.calcs.calcs import STRUCT_LOSS
from core_hazimp.config import (LOADWINDTCRM, TEMPLATE, WINDV1, SAVE, WINDV2,
                                FLOODFABRICV1, LOADFLOODASCII)
from core_hazimp import parallel


class TestWind(unittest.TestCase):

    """
    Do large system based tests.
    """

    def test_const_test(self):
        # First test running an end to end wind test based
        # on a config dictionary, no template

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        vul_filename = os.path.join(misc.RESOURCE_DIR,
                                    'synthetic_domestic_wind_vul_curves.xml')
        config = {
            'jobs': [LOADCSVEXPOSURE, LOADRASTER, LOADXMLVULNERABILITY,
                     SIMPLELINKER, SELECTVULNFUNCTION, LOOKUP, STRUCT_LOSS,
                     SAVEALL],
            LOADCSVEXPOSURE: {'file_name': exp_filename,
                              'exposure_latitude': 'LATITUDE',
                              'exposure_longitude': 'LONGITUDE'},
            LOADRASTER: {'file_list': [wind_filename],
                         'attribute_label':
                         '0.2s gust at 10m height m/s'},
            LOADXMLVULNERABILITY: {'file_name': vul_filename},
            SIMPLELINKER: {'vul_functions_in_exposure': {
                'domestic_wind_2012': 'WIND_VULNERABILITY_FUNCTION_ID'}},
            SELECTVULNFUNCTION: {'variability_method': {
                'domestic_wind_2012': 'mean'}},
            SAVEALL: {'file_name': f.name}}

        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)

    def test_wind_v2_template(self):
        # Test running an end to end cyclone test based
        # on a wind config template.

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        config = {
            TEMPLATE: WINDV2,
            LOADCSVEXPOSURE: {'file_name': exp_filename,
                              'exposure_latitude': 'LATITUDE',
                              'exposure_longitude': 'LONGITUDE'},
            LOADWINDTCRM: [wind_filename],
            SAVE: f.name}

        context = hazimp.main(config_dic=config)

        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)

    def test_wind_v2_templateII(self):
        # Test running an end to end cyclone test based
        # on a wind config template.
        # Use a string to describe the hazard file, not a list of strings

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        config = {
            TEMPLATE: WINDV2,
            LOADCSVEXPOSURE: {'file_name': exp_filename,
                              'exposure_latitude': 'LATITUDE',
                              'exposure_longitude': 'LONGITUDE'},
            LOADWINDTCRM: wind_filename,
            SAVE: f.name}

        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)

    def test_wind_yaml(self):
        # Test running an end to end cyclone test based
        # on a wind config template.

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')

        # The output file
        f_out = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        # The config file
        f = tempfile.NamedTemporaryFile(
            suffix='.yaml',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        print(TEMPLATE + ': ' + WINDV2, file=f)
        print(LOADCSVEXPOSURE + ': ', file=f)
        print('  file_name: ' + exp_filename, file=f)
        print('  exposure_latitude: LATITUDE', file=f)
        print('  exposure_longitude: LONGITUDE', file=f)
        print(LOADWINDTCRM + ': [' + wind_filename + ']', file=f)
        print(SAVE + ': ' + f_out.name, file=f)
        f.close()

        context = hazimp.main(config_file=f.name)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f_out.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)
        os.remove(f_out.name)

    def test_wind_v1_template_csv(self):
        # Test running an end to end cyclone test based
        # on a wind config template.

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.csv',
            prefix='HAZIMP_flood_scenarios_test_const',
            delete=False)

        resource_dir = os.path.join(misc.EXAMPLE_DIR, 'flood')
        exp_filename = os.path.join(resource_dir,
                                    'small_exposure.csv')
        haz_filename = os.path.join(resource_dir, 'depth_small_synthetic.txt')
        config = {
            TEMPLATE: FLOODFABRICV1,
            LOADCSVEXPOSURE: {'file_name': exp_filename,
                              'exposure_latitude': 'LATITUDE',
                              'exposure_longitude': 'LONGITUDE'},
            LOADFLOODASCII: [haz_filename],
            SAVE: f.name}

        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = misc.csv2dict(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)

#-------------------------------------------------------------
if __name__ == "__main__":

    SUITE = unittest.makeSuite(TestWind, 'test')
    SUITE = unittest.makeSuite(TestWind, 'test_wind_v1_template_csv')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

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
from core_hazimp.config import (TEMPLATE, SAVE, FLOODFABRICV1, LOADFLOODASCII,
                                FLOODFABRICV2)
from core_hazimp import parallel


class TestWind(unittest.TestCase):
    """
    Do large system based tests.
    """

    def test_flood_v1_template(self):
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


    def test_flood_v1_template_list(self):
        # Test running an end to end wind test based
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
        config = [{TEMPLATE: FLOODFABRICV2},
                  {LOADCSVEXPOSURE: {'file_name': exp_filename,
                                     'exposure_latitude': 'LATITUDE',
                                     'exposure_longitude': 'LONGITUDE'}},
                  {LOADFLOODASCII: [haz_filename]},
                  {SAVE: f.name}]

        context = hazimp.start(config_list=config)
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
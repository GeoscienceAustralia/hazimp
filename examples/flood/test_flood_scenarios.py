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
from core_hazimp.calcs.calcs import FLOOR_HEIGHT
from core_hazimp.jobs.jobs import (LOADCSVEXPOSURE)
from core_hazimp.templates import (SAVE, LOADFLOODASCII, FLOODFABRICV2,
                                   TEMPLATE, FLOODCONTENTSV2, CALCCONTLOSS,
                                   CALCSTRUCTLOSS, REP_VAL_NAME)
from core_hazimp import templates as flood_conts
from core_hazimp import parallel


class TestFlood(unittest.TestCase):

    """
    Do a large system based test.
    """

    def test_flood_fabric_v2_template_list(self):
        # Test running an end to end  test based
        # on a config template.

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
                  {FLOOR_HEIGHT: .3},
                  {LOADFLOODASCII: [haz_filename]},
                  {CALCSTRUCTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
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

    def test_flood_struct_yaml_list(self):
        # Test running an end to end flood test based
        # on a flood config template.
        # IF YOU CHANGE THIS CHANGE list_flood_v2.yaml as well

        flood_dir = os.path.join(misc.EXAMPLE_DIR, 'flood')
        exp_filename = os.path.join(flood_dir,
                                    'small_exposure.csv')
        flood_filename = os.path.join(flood_dir, 'depth_small_synthetic.txt')

        # The output file
        f_out = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_flood_scenarios_test_const',
            delete=False)

        # The config file
        f = tempfile.NamedTemporaryFile(
            suffix='.yaml',
            prefix='HAZIMP_flood_scenarios_test_const',
            delete=False)

        print(' - ' + TEMPLATE + ': ' + FLOODFABRICV2, file=f)
        print(' - ' + LOADCSVEXPOSURE + ': ', file=f)
        print('      file_name: ' + exp_filename, file=f)
        print('      exposure_latitude: LATITUDE', file=f)
        print('      exposure_longitude: LONGITUDE', file=f)
        print(' - ' + FLOOR_HEIGHT + ': .3', file=f)
        a_str = ' - ' + LOADFLOODASCII + ': [' + flood_filename + ']'
        print(a_str, file=f)
        print(' - ' + CALCSTRUCTLOSS + ': ', file=f)
        print('      ' + REP_VAL_NAME + ': ' + 'REPLACEMENT_VALUE', file=f)
        print(' - ' + SAVE + ': ' + f_out.name, file=f)
        f.close()

        context = hazimp.start(config_file=f.name)
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

    def test_flood_contents_v2_template_list(self):
        # Test running an end to end  test based
        # on a config template.
        """
        Failing with this error.

        FIXME

        Traceback (most recent call last):
  File "/nas/mnh/georisk_models/hazard_impact/sandpits/duncan/
  github_hazimp/examples/flood/test_flood_scenarios.py",
  line 145, in test_flood_contents_v2_template_list
    context.exposure_att['structural_loss'],
KeyError: 'structural_loss'

        Part of fixing this is knowing what the answer should be...
        """

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.csv',
            prefix='HAZIMP_flood_scenarios_test_const',
            delete=False)
        resource_dir = os.path.join(misc.EXAMPLE_DIR, 'flood')
        exp_filename = os.path.join(resource_dir,
                                    'small_exposure.csv')
        haz_filename = os.path.join(resource_dir, 'depth_small_synthetic.txt')
        config = [{TEMPLATE: FLOODCONTENTSV2},
                  {LOADCSVEXPOSURE: {'file_name': exp_filename,
                                     'exposure_latitude': 'LATITUDE',
                                     'exposure_longitude': 'LONGITUDE'}},
                  {FLOOR_HEIGHT: .3},
                  {LOADFLOODASCII: [haz_filename]},
                  {flood_conts.INSURE_PROB: {flood_conts.INSURED: 0.3,
                                             flood_conts.UNINSURED: 0.7}},
                  {flood_conts.CONT_ACTIONS: {flood_conts.SAVE_CONT: 0.5,
                                              flood_conts.NO_ACTION_CONT: 0.4,
                                              flood_conts.EXPOSE_CONT: 0.1}},
                  {CALCCONTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
                  {SAVE: f.name}]

        context = hazimp.start(config_list=config)
        self.assertTrue(allclose(
            context.exposure_att['contents_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = misc.csv2dict(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        os.remove(f.name)
# -------------------------------------------------------------
if __name__ == "__main__":

    SUITE = unittest.makeSuite(TestFlood, 'test')
    # SUITE = unittest.makeSuite(TestFlood, '')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

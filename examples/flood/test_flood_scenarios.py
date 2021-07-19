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

import unittest
import os
import tempfile
import numpy
from scipy import allclose

from hazimp import misc
from hazimp import main
from hazimp.calcs.calcs import FLOOR_HEIGHT
from hazimp.jobs.jobs import (LOADCSVEXPOSURE)
from hazimp.templates import (SAVE, FLOODFABRICV2,
                              TEMPLATE, FLOODCONTENTSV2, CALCCONTLOSS,
                              CALCSTRUCTLOSS, REP_VAL_NAME, HAZARDRASTER)
from hazimp import templates as flood_conts
from hazimp import parallel


class TestFlood(unittest.TestCase):

    """
    Do a large system based test.
    """

    def test_flood_fabric_v2_template_list(self):
        # Test running an end to end  test based
        # on a config template.

        # The output file
        f = tempfile.NamedTemporaryFile(
            mode='w',
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
                  {HAZARDRASTER: [haz_filename]},
                  {CALCSTRUCTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
                  {SAVE: f.name}]

        context = main.start(config_list=config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = misc.csv2dict(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))

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
            mode='w',
            suffix='.npz',
            prefix='HAZIMPt_flood_scenarios_test_const',
            delete=False)

        # The config file
        f = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            prefix='HAZIMP_flood_scenarios_test_const',
            delete=False)

        print(' - ' + TEMPLATE + ': ' + FLOODFABRICV2, file=f)
        print(' - ' + LOADCSVEXPOSURE + ': ', file=f)
        print('      file_name: ' + exp_filename, file=f)
        print('      exposure_latitude: LATITUDE', file=f)
        print('      exposure_longitude: LONGITUDE', file=f)
        print(' - ' + FLOOR_HEIGHT + ': .3', file=f)
        a_str = ' - ' + HAZARDRASTER + ': [' + flood_filename + ']'
        print(a_str, file=f)
        print(' - ' + CALCSTRUCTLOSS + ': ', file=f)
        print('      ' + REP_VAL_NAME + ': ' + 'REPLACEMENT_VALUE', file=f)
        print(' - ' + SAVE + ': ' + f_out.name, file=f)
        f.close()

        context = main.start(config_file=f.name)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f_out.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))

    def test_flood_contents_v2_template_list(self):
        # Test running an end to end  test based
        # on a config template.
        # Note, removing randomness for testing purposes

        # The output file
        f = tempfile.NamedTemporaryFile(
            mode='w',
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
                  {HAZARDRASTER: [haz_filename]},
                  {flood_conts.INSURE_PROB: {flood_conts.INSURED: 1.0,
                                             flood_conts.UNINSURED: 0.0}},
                  {flood_conts.CONT_ACTIONS: {flood_conts.SAVE_CONT: 0.0,
                                              flood_conts.NO_ACTION_CONT: 0.0,
                                              flood_conts.EXPOSE_CONT: 1.0}},
                  {CALCCONTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
                  {SAVE: f.name}]

        context = main.start(config_list=config)

        # These don't work on parallelised tests
        # if they are wrong the error will flow
        # on and be caught in the contents_loss
        # self.assertTrue(allclose(
        #     context.exposure_att['calced_haz'][[0, 1, 3]],
        #     context.exposure_att['water_depth'][[0, 1, 3]]))
        #
        # index = 'water depth above ground floor (m)'
        # self.assertTrue(allclose(
        #     context.exposure_att['calced_floor_depth'][[0, 1, 3]],
        #     context.exposure_att[index][[0, 1, 3]]))

        # print ('file name', f.name)

        # self.assertTrue(numpy.array_equal(
        #    context.exposure_att['calced_CONTENTS_FLOOD_FUNCTION_ID'],
        #    context.exposure_att['CONTENTS_FLOOD_FUNCTION_ID']))

        self.assertTrue(allclose(
            context.exposure_att['calced_contents_loss_ratio'],
            context.exposure_att['contents']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = misc.csv2dict(f.name)
            self.assertTrue(allclose(exp_dict['contents_loss'],
                                     exp_dict['calced_contents_loss']))
        # os.remove(f.name)


# -------------------------------------------------------------
if __name__ == "__main__":

    SUITE = unittest.makeSuite(TestFlood, 'test')
    # SUITE = unittest.makeSuite(TestFlood, '')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

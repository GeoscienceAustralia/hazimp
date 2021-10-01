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
from time import sleep
import numpy

from scipy import allclose

from hazimp import misc
from hazimp import main
from hazimp.jobs.jobs import (LOADRASTER, LOADCSVEXPOSURE,
                              LOADXMLVULNERABILITY, SIMPLELINKER,
                              SELECTVULNFUNCTION,
                              LOOKUP, SAVEALL)
from hazimp.calcs import calcs
from hazimp import parallel
from hazimp.templates import (SAVE, LOADWINDTCRM, WINDV3,
                              TEMPLATE, DEFAULT, CALCSTRUCTLOSS,
                              REP_VAL_NAME, VULNFILE, VULNSET)


class TestWind(unittest.TestCase):

    """
    Do large system based tests.
    """

    def test_const_test(self):
        # First test running an end to end wind test based
        # on a config list, no template

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
        sim_at = {'domestic_wind_2012': 'WIND_VULNERABILITY_FUNCTION_ID'}
        slv_at = {'domestic_wind_2012': 'mean'}
        a_config = [
            {TEMPLATE: DEFAULT},
            {LOADCSVEXPOSURE: {'file_name': exp_filename,
                               'exposure_latitude': 'LATITUDE',
                               'exposure_longitude': 'LONGITUDE'}},
            {LOADRASTER: {'file_list': [wind_filename],
                          'attribute_label':
                          '0.2s gust at 10m height m/s'}},
            {LOADXMLVULNERABILITY: {'file_name':
                                    vul_filename}},
            {SIMPLELINKER: {'vul_functions_in_exposure': sim_at}},
            {SELECTVULNFUNCTION: {'variability_method': slv_at}},
            {LOOKUP: None},
            {calcs.STRUCT_LOSS: None},
            {SAVEALL: {'file_name': f.name}}]

        context = main.start(config_list=a_config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))
        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f.name)

            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        # os.remove(f.name)

    def test_wind_v3_template(self):
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
        vul_filename = os.path.join(misc.RESOURCE_DIR,
                                    'synthetic_domestic_wind_vul_curves.xml')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        a_config = [{TEMPLATE: WINDV3},
                    {VULNFILE: vul_filename},
                    {VULNSET: 'domestic_wind_2012'},
                    {LOADCSVEXPOSURE: {'file_name': exp_filename,
                                       'exposure_latitude': 'LATITUDE',
                                       'exposure_longitude': 'LONGITUDE'}},
                    {LOADWINDTCRM: [wind_filename]},
                    {CALCSTRUCTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
                    {SAVE: f.name}]

        context = main.start(config_list=a_config)

        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = numpy.load(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
        # os.remove(f.name)

    def test_wind_yaml_v3_list(self):
        # Test running an end to end cyclone test based
        # on a wind config template.

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        vul_filename = os.path.join(misc.RESOURCE_DIR,
                                    'synthetic_domestic_wind_vul_curves.xml')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')

        # The output file
        f_out = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        # The config file
        f = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            prefix='HAZIMP_wind_scenarios_test_const',
            delete=False)

        f.write(f" - {TEMPLATE}: {WINDV3}\n")
        f.write(f" - {VULNFILE}: {vul_filename}\n")
        f.write(f" - {VULNSET}: domestic_wind_2012\n")
        f.write(f" - {LOADCSVEXPOSURE}:\n")
        f.write(f"      file_name: {exp_filename}\n")
        f.write("      exposure_latitude: LATITUDE\n")
        f.write("      exposure_longitude: LONGITUDE\n")
        f.write(f" - {LOADWINDTCRM}: [{wind_filename}]\n")
        f.write(f" - {CALCSTRUCTLOSS}: \n")
        f.write(f"      {REP_VAL_NAME}: REPLACEMENT_VALUE\n")
        f.write(f" - {SAVE}: {f_out.name}\n")
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
        # os.remove(f.name)
        # os.remove(f_out.name)

    def test_wind_v3_template_list_csv(self):
        # Test running an end to end cyclone test based
        # on a wind config template.

        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.csv',
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)

        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir,
                                    'syn_small_exposure_tcrm.csv')
        vul_filename = os.path.join(misc.RESOURCE_DIR,
                                    'synthetic_domestic_wind_vul_curves.xml')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        a_config = [{TEMPLATE: WINDV3},
                    {LOADCSVEXPOSURE:
                     {'file_name': exp_filename,
                      'exposure_latitude': 'LATITUDE',
                      'exposure_longitude': 'LONGITUDE'}},
                    {VULNFILE: vul_filename},
                    {VULNSET: 'domestic_wind_2012'},
                    {LOADWINDTCRM: [wind_filename]},
                    {CALCSTRUCTLOSS: {REP_VAL_NAME: 'REPLACEMENT_VALUE'}},
                    {SAVE: f.name}]

        context = main.start(config_list=a_config)
        self.assertTrue(allclose(
            context.exposure_att['structural_loss'],
            context.exposure_att['calced-loss']))

        # Only the head node writes a file
        if parallel.STATE.rank == 0:
            exp_dict = misc.csv2dict(f.name)
            self.assertTrue(allclose(exp_dict['structural_loss'],
                                     exp_dict['calced-loss']))
            # Failing this shows how versions of numpy
            # less than 1.8 reduce the
            # number of significant figures in the output
            self.assertTrue(allclose(exp_dict['exposure_latitude'],
                                     [-22.99, -23.01, -22.99, -23.99, -23]))
        # os.remove(f.name)


# -------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestWind, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

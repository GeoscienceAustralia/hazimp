# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Geoscience Australia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the config module.
"""

import unittest
import tempfile
import os

from core_hazimp import config
from core_hazimp.calcs import calcs
from core_hazimp.jobs import jobs


class TestConfig(unittest.TestCase):

    """
    Test the config module
    """

    def test_get_job_or_calc(self):
        # messy test.  Relies on calcs.py and jobs.py
        name = 'add_test'
        job = config._get_job_or_calc(name)  # pylint: disable=W0212
        self.assertIsInstance(job, calcs.Add)

        name = 'const_test'
        job = config._get_job_or_calc(name)  # pylint: disable=W0212
        self.assertIsInstance(job, jobs.ConstTest)

    def test_job_reader(self):
        the_config = [{'add_test': None}]
        actual = config.instance_builder(the_config)
        self.assertEqual(calcs.CALCS['add_test'], actual[0].job_instance)

    def test_file_can_open(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt',
            prefix='HAZIMPtest_config',
            delete=False)
        f.write('yeah\n')
        f.close()

        self.assertTrue(config.file_can_open(f.name))
        os.remove(f.name)

    def test_file_can_openII(self):
        self.assertFalse(config.file_can_open("/there/should/be/no/file.txt"))

    def test_file_can_openIII(self):
        junk_files = []
        for _ in range(3):
            # Write a file to test
            f = tempfile.NamedTemporaryFile(
                suffix='.txt',
                prefix='HAZIMPtest_config',
                delete=False)
            f.write('yeah\n')
            f.close()
            junk_files.append(f)

        config_dic = {
            'dove': {'file_name': junk_files[0].name},
            'eagle': {'file_list': [junk_files[1].name, junk_files[2].name]},
            'save': {'file_name': 'not_here'},
            'save_all': {'file_list': ['still_not_here']}
        }
        self.assertTrue(config.check_files_to_load(config_dic))

        for handle in junk_files:
            os.remove(handle.name)

    def test_file_can_openIV(self):

        # Test that an Error is raised if the files aren't there
        junk_files = []
        for _ in range(3):
            # Write a file to test
            f = tempfile.NamedTemporaryFile(
                suffix='.txt',
                prefix='HAZIMPtest_config',
                delete=False)
            f.write('yeah\n')
            f.close()
            junk_files.append(f)

        for handle in junk_files:
            os.remove(handle.name)

        config_dic = {
            'dove': {'file_name': junk_files[0].name},
            'eagle': {'file_list': [junk_files[1].name, junk_files[2].name]}
        }

        self.assertRaises(RuntimeError, config.check_files_to_load, config_dic)
        self.assertRaises(RuntimeError, config.validate_config, config_dic)

    def test_check_1st_level_keys(self):
        config_dic = {'foo': 12}
        self.assertRaises(RuntimeError, config.check_1st_level_keys,
                          config_dic)

    def test_check_attributes(self):
        config_dic = {jobs.JOBSKEY: 12}
        config.check_attributes(config_dic)

        config_dic = {jobs.LOADCSVEXPOSURE: {
            'file_name': 'yeah',
            'exposure_latitude': 'latitude',
            'exposure_longitude': 'longitude'}}
        config.check_attributes(config_dic)

        config_dic = {jobs.LOADCSVEXPOSURE: {'file_name': 'yeah'}}
        config.check_attributes(config_dic)

        config_dic = {
            'jobs': [jobs.LOADCSVEXPOSURE, jobs.LOADRASTER,
                     jobs.LOADXMLVULNERABILITY,
                     jobs.SIMPLELINKER, jobs.SELECTVULNFUNCTION, jobs.LOOKUP,
                     calcs.STRUCT_LOSS,
                     jobs.SAVEALL],
            jobs.LOADCSVEXPOSURE: {'file_name': 'yeah',
                                   'exposure_latitude': 'latitude',
                                   'exposure_longitude': 'longitude'},
            jobs.LOADRASTER: {'file_list': ['ha'],
                              'attribute_label':
                              '0.2s gust at 10m height m/s'},
            jobs.LOADXMLVULNERABILITY: {'file_name': 'grolovolo'},
            jobs.SIMPLELINKER: {'vul_functions_in_exposure': {
                'domestic_wind_2012': 'wind_vulnerability_model'}},
            jobs.SELECTVULNFUNCTION: {'variability_method': {
                'domestic_wind_2012': 'mean'}},
            jobs.SAVEALL: {'file_name': 'fash'}}
        config.check_attributes(config_dic)

        config_dic = {jobs.LOADCSVEXPOSURE: {
            'file_!name': 'yeah',
            'exposure_latitude': 'latitude',
            'exposure_longitude': 'longitude'}}
        self.assertRaises(RuntimeError, config.check_attributes, config_dic)

    def test_check_attributesII(self):
        config_dic = {jobs.LOADCSVEXPOSURE: {
            'file_name': 'yeah',
            'yeahe': 'latitude',
            'expode': 'longitude'}}
        self.assertRaises(RuntimeError, config.check_attributes, config_dic)

    def test_find_atts(self):
        config_list = [{jobs.LOADCSVEXPOSURE: {
            'file_name': 'yeah',
            'yeahe': 'latitude',
            'expode': 'longitude'}}]
        self.assertRaises(RuntimeError, config.find_atts, config_list, 'foo')

    def test_find_attsII(self):
        actual_atts = {'file_name': 'yeah',
                       'yeahe': 'latitude',
                       'expode': 'longitude'}
        config_list = [{jobs.LOADCSVEXPOSURE: actual_atts}]
        atts = config.find_atts(config_list, jobs.LOADCSVEXPOSURE)
        self.assertEqual(atts, actual_atts)

# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestConfig, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

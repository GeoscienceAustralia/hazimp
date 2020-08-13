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

from hazimp import config
from hazimp.calcs import calcs
from hazimp.config_build import (find_atts, _get_job_or_calc,
                                 check_1st_level_keys, file_can_open,
                                 check_files_to_load, check_attributes)
from hazimp.jobs import jobs


class TestConfig(unittest.TestCase):

    """
    Test the config module
    """

    def test_get_job_or_calc(self):
        # messy test.  Relies on calcs.py and jobs.py
        name = 'add_test'
        job = _get_job_or_calc(name)  # pylint: disable=W0212
        self.assertIsInstance(job, calcs.Add)

        name = 'const_test'
        job = _get_job_or_calc(name)  # pylint: disable=W0212
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
            delete=False,
            mode='w+t')
        f.write('yeah\n')
        f.close()

        self.assertTrue(file_can_open(f.name))
        os.remove(f.name)

    def test_file_can_openII(self):
        self.assertFalse(file_can_open("/there/should/be/no/file.txt"))

    def test_check_files_to_load(self):
        junk_files = []
        for _ in range(3):
            # Write a file to test
            f = tempfile.NamedTemporaryFile(
                suffix='.txt',
                prefix='HAZIMPtest_config',
                delete=False,
                mode='w+t')
            f.write('yeah\n')
            f.close()
            junk_files.append(f)

        atts = {'file_name': junk_files[0].name}
        self.assertTrue(check_files_to_load(atts))

        atts = {'file_list': [junk_files[1].name, junk_files[2].name]}
        self.assertTrue(check_files_to_load(atts))

        atts = {'file_name': 'not_here'}
        self.assertTrue(check_files_to_load(atts))

        atts = {'file_list': ['still_not_here']}
        self.assertTrue(check_files_to_load(atts))

        for handle in junk_files:
            os.remove(handle.name)

    def test_check_1st_level_keys(self):

        # Hard to do a good test for this function.
        self.assertRaises(RuntimeError, check_1st_level_keys,
                          'yeah')

    def test_check_attributes(self):
        atts = {'file_name': 'yeah',
                'exposure_latitude': 'latitude',
                'exposure_longitude': 'longitude'}
        inst = jobs.JOBS[jobs.LOADCSVEXPOSURE]
        self.assertTrue(check_attributes(inst, atts))

    def test_check_attributesII(self):
        atts = {'file_name': 'yeah', 'yeahe': 'latitude'}
        inst = jobs.JOBS[jobs.LOADCSVEXPOSURE]
        self.assertRaises(RuntimeError, check_attributes, inst, atts)

    def test_check_attributesIII(self):
        atts = {'file_names': 'yeah', 'yeahe': 'latitude'}
        inst = jobs.JOBS[jobs.LOADCSVEXPOSURE]
        self.assertRaises(RuntimeError, check_attributes, inst, atts)

    def test_check_attributesIV(self):
        atts = {'file_name': 'yeah'}
        inst = jobs.JOBS[jobs.LOADCSVEXPOSURE]
        self.assertTrue(check_attributes(inst, atts))

    def test_check_attributesV(self):
        atts = {'variability_method': {'domestic_wind_2012': 'mean'}}
        inst = jobs.JOBS[jobs.SELECTVULNFUNCTION]
        self.assertTrue(check_attributes(inst, atts))

    def test_find_atts(self):
        config_list = [{jobs.LOADCSVEXPOSURE: {
            'file_name': 'yeah',
            'yeahe': 'latitude',
            'expode': 'longitude'}}]
        self.assertRaises(RuntimeError, find_atts, config_list, 'foo')

    def test_find_attsII(self):
        actual_atts = {'file_name': 'yeah',
                       'yeahe': 'latitude',
                       'expode': 'longitude'}
        config_list = [{jobs.LOADCSVEXPOSURE: actual_atts}]
        atts = find_atts(config_list, jobs.LOADCSVEXPOSURE)
        self.assertEqual(atts, actual_atts)

# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestConfig, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

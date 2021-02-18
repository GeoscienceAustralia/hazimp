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

import os
import tempfile
import unittest
from pathlib import Path

from hazimp import config
from hazimp.calcs import calcs
from hazimp.calcs.calcs import WATER_DEPTH
from hazimp.config import instance_builder, read_config_file
from hazimp.config_build import (_get_job_or_calc,
                                 check_1st_level_keys, file_can_open,
                                 check_files_to_load, check_attributes, find_attributes)
from hazimp.jobs import jobs
from hazimp.jobs.jobs import LOADRASTER, SAVEALL, LoadRaster, SaveExposure
from tests import CWD


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

    def test_instance_builder_bad_format(self):
        with self.assertRaises(RuntimeError) as context:
            instance_builder(['template'])

        self.assertEqual(
            '\nConfig bad format. Forgotten dash? Two key dictionary?\ntemplate \n',
            str(context.exception)
        )

    def test_instance_builder_invalid_template(self):
        with self.assertRaises(RuntimeError) as context:
            instance_builder([{
                'template': 'invalid'
            }])

        self.assertEqual(
            'Invalid template name, invalid in config file.',
            str(context.exception)
        )

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

    def test_find_attributes_fails(self):
        config = {jobs.LOADCSVEXPOSURE: {'file_name': 'exposure.csv'}}

        with self.assertRaises(RuntimeError) as context:
            find_attributes(config, 'invalid_key')

        self.assertEqual(
            str(context.exception),
            'Mandatory key not found in config file: invalid_key'
        )

    def test_find_attributes_succeeds(self):
        expected_attributes = {'file_name': 'exposure.csv'}

        config = {jobs.LOADCSVEXPOSURE: expected_attributes}
        attributes = find_attributes(config, jobs.LOADCSVEXPOSURE)
        self.assertEqual(attributes, expected_attributes)

    def test_find_attributes_by_lesser_preference(self):
        expected_attributes = {'file_name': 'exposure.csv'}

        config = {jobs.LOADCSVEXPOSURE: expected_attributes}
        attributes = find_attributes(config, [jobs.LOADRASTER, jobs.LOADCSVEXPOSURE])
        self.assertEqual(attributes, expected_attributes)

    def test_instansiate_jobs_without_template(self):
        config = [
            {LOADRASTER: {
                'attribute_label': WATER_DEPTH,
                'file_list': ['raster1.tif', 'raster2.tif']
            }},
            {SAVEALL: {
                'file_name': 'output.csv'
            }}
        ]

        [raster_job, save_job] = instance_builder(config)

        self.assertIsInstance(raster_job.job_instance, LoadRaster)
        self.assertIsInstance(save_job.job_instance, SaveExposure)

    def test_read_yaml_file(self):
        template = read_config_file(str(CWD / 'data/template.yaml'))

        self.assertEqual([{'template': 'default'}, {'key': 'value'}], template)


if __name__ == "__main__":
    Suite = unittest.makeSuite(TestConfig, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

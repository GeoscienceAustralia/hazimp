# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Geoscience Australia

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
# pylint: disable=E1123
# pylint says;  Passing unexpected keyword argument 'delete' in function call
# I need to pass it though.
# pylint: disable=R0801


"""
Test the data in resources.  Can it be loaded?
"""

import os
import unittest
from glob import glob

from hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file
from hazimp.misc import RESOURCE_DIR
from hazimp.validator import Validator, NRML_SCHEMA
from tests import CWD


class TestResources(unittest.TestCase):

    """
    Test the data in resources.
    """

    def test_domestic_wind_vul_curves(self):
        vuln_sets = vuln_sets_from_xml_file(
            [os.path.join(RESOURCE_DIR,
                          'content_flood_avg_curve.xml')])
        set_id = vuln_sets["contents_domestic_flood_2012"]
        actual = set_id.intensity_measure_type
        self.assertEqual(actual, "water depth above ground floor (m)")

        # Check the first loss value of the last model
        vul_funct = set_id.vulnerability_functions['FCM1_INSURED_NOACTION']
        self.assertAlmostEqual(vul_funct.mean_loss[0], 0.0)

    def test_resources_pass_validation(self):
        for resource in glob(str(CWD / '../resources/*.xml')):
            filename = os.path.basename(resource)
            with self.subTest(filename):
                try:
                    validator = Validator(NRML_SCHEMA)
                    validator.validate(resource)
                except AssertionError:
                    self.fail(f'{filename} should validate against {NRML_SCHEMA}')


if __name__ == "__main__":
    Suite = unittest.makeSuite(TestResources, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

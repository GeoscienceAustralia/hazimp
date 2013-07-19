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

import unittest
import os

from core_hazimp.misc import RESOURCE_DIR
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file


class TestResources(unittest.TestCase):
    """
    Test the data in resources.
    """
    def test_domestic_wind_vul_curves(self):
        vuln_sets = vuln_sets_from_xml_file(
            os.path.join(RESOURCE_DIR,
                         'domestic_wind_vul_curves.xml'))
        actual = vuln_sets["domestic_wind_2012"].intensity_measure_type
        self.assertEqual(actual, "0.2s gust at 10m height m/s")

        # Check the first loss value of the last model
        vul_funct = vuln_sets["domestic_wind_2012"].vulnerability_functions[
            'dw306']
        self.assertAlmostEqual(vul_funct.mean_loss[0], 0.0)

#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestResources, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

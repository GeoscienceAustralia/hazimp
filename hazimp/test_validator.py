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

"""
Test XML file validation
"""

import os
import tempfile
import unittest

from hazimp.validator import Validator, NRLM_SCHEMA

valid_xml = '''<?xml version='1.0' encoding='utf-8'?>
<nrml xmlns="http://openquake.org/xmlns/nrml/0.4"
    xmlns:gml="http://www.opengis.net/gml">
    <vulnerabilityModel>
        <discreteVulnerabilitySet vulnerabilitySetID="domestic_wind_2012"
            assetCategory="" lossCategory="structural_loss_ratio">
            <IML IMT="0.2s gust at 10m height m/s">
                17.0 20.0 22.0 24.0 26.0 28.0 30.0 32.0 34.0 36.0 38.0
                40.0 42.0 44.0 46.0 48.0 50.0 52.0 54.0 56.0 58.0 60.0
                62.0 64.0 66.0 68.0 70.0 72.0 74.0 76.0 78.0 80.0 82.0
                84.0 86.0 88.0 90.0 100.0
            </IML>
            <discreteVulnerability vulnerabilityFunctionID="dw1"
                probabilisticDistribution="LN">
                <lossRatio>
                    0 6.00E-05 0.00012 0.00024 0.00044 0.00081 0.0014 0.0023
                    0.0038 0.006 0.0092 0.014 0.02 0.03 0.042 0.058 0.078 0.1
                    0.14 0.18 0.23 0.3 0.36 0.44 0.52 0.61 0.69 0.77 0.84 0.9
                    0.93 0.96 0.98 0.985 0.99 0.993 0.995 1
                </lossRatio>
                <coefficientsVariation>
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
                    0 0 0 0 0 0 0 0 0 0
                </coefficientsVariation>
            </discreteVulnerability>
        </discreteVulnerabilitySet>
    </vulnerabilityModel>
</nrml>'''

invalid_xml = '''<?xml version='1.0' encoding='utf-8'?>
<invalid></invalid>'''


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = Validator(NRLM_SCHEMA)

    def test_validator_succeeds(self):
        try:
            self.run_with_xml(valid_xml, self.validator.validate)
        except AssertionError:
            self.fail('Expected no schema validation errors')

    def test_validator_fails(self):
        with self.assertRaises(AssertionError):
            self.run_with_xml(invalid_xml, self.validator.validate)

    def run_with_xml(self, xml, f):
        fd, path = tempfile.mkstemp()

        try:
            with os.fdopen(fd, 'w') as file:
                file.write(xml)
                file.flush()

                f(path)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()

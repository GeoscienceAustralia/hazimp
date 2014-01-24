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
# pylint: disable=E1123
# W0104: 61:TestCreateVulnXML.test1_csv_curve2nrml: Seems to have no effect
# pylint: disable=W0104

"""
Test the create vulnerability module.
"""

import unittest
import tempfile
import os

from scipy import asarray, allclose

# W0403: 37: Relative import 'create_vuln_xml', should be 'curve_data.yadda'
# pylint: disable=w0403
import create_vuln_xml
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file

def determine_this_file_path(file=__file__):
    """
    Workout a path string that describes the directory this file is in.
    """
    current_dir, tail = os.path.split(file)
    return os.path.abspath(current_dir)

class TestCreateVulnXML(unittest.TestCase):

    """
    Test the Raster module
    """

    def test1_csv_curve2nrml(self):
        # Write a file to test
        # pylint: disable=R0801
        f = tempfile.NamedTemporaryFile(suffix='.csv',
                                        prefix='test_creazte_vuln_xml',
                                        delete=False)
        f.write('vulnerabilityFunctionID, vulnerabilitySetID, assetCategory,')
        f.write(' lossCategory, Alpha, Beta, IMT, IML, 17, 20\r\n')
        f.write('dw1, d2012, , structural, 0.1, 0.01,')
        f.write(' gust, 17, 0.01, 0.1 \r\n')
        f.write('dw2, d2012, , structural, 0.2, 0.02,')
        f.write(' gust, 20, 0.02, 0.2 \r\n')
        f.close
        csv_name = f.name
        f = tempfile.NamedTemporaryFile(suffix='.xml',
                                        prefix='test_creazte_vuln_xml',
                                        delete=False)
        xml_name = f.name
        create_vuln_xml.csv_curve2nrml(csv_name, xml_name)
        vuln_sets = vuln_sets_from_xml_file(xml_name)

        self.assertTrue(allclose(vuln_sets["d2012"].intensity_measure_level,
                                 asarray([17, 20])))
        self.assertEqual(vuln_sets["d2012"].intensity_measure_type, "gust")
        self.assertEqual(vuln_sets["d2012"].vulnerability_set_id, "d2012")
        self.assertEqual(vuln_sets["d2012"].asset_category, "")
        self.assertEqual(vuln_sets["d2012"].loss_category, "structural")

        loss_rs = {"dw1": asarray([0.01, 0.1]),
                   "dw2": asarray([0.02, 0.2])}
        covs = {"dw1": asarray([0., 0.]),
                "dw2": asarray([0., 0.])}

        for key in loss_rs:
            vul_funct = vuln_sets["d2012"].vulnerability_functions[key]
            self.assertTrue(allclose(vul_funct.mean_loss,
                                     loss_rs[key]))
            self.assertTrue(allclose(vul_funct.coefficient_of_variation,
                                     covs[key]))

        os.remove(csv_name)
        os.remove(xml_name)

    def test1_validate_excel_curve_data(self):
        dirs = determine_this_file_path()
        excel_file = 'Flood_2012_test.xlsx'
        excel_file = os.path.join(dirs, excel_file)
        valid = create_vuln_xml.validate_excel_curve_data(excel_file)
        self.assertTrue(valid)
        
    def test1_read_excel_curve_data(self):
        dirs = determine_this_file_path()
        excel_file = 'Flood_2012_test.xlsx'
        excel_file = os.path.join(dirs, excel_file)
        curves, depths = create_vuln_xml.read_excel_curve_data(excel_file)
#-------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestCreateVulnXML, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

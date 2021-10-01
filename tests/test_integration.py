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
Test how all of the modules work in a standard workflow.
"""

import unittest
import tempfile
import os

from scipy import allclose

from hazimp import main
from hazimp.jobs import jobs
from hazimp import parallel


def build_example_building_vulnerability():
    """Build an example xml file.
    If you call this remember to delete the file;  os.remove(filename).

    Returns:
        The name of the file
    """
    str2 = """<?xml version='1.0' encoding='utf-8'?>
<nrml xmlns="http://openquake.org/xmlns/nrml/0.5"
      xmlns:gml="http://www.opengis.net/gml">

    <vulnerabilityModel id="EQ_building"
     assetCategory="not_used"
     lossCategory="building_loss">
            <vulnerabilityFunction id="SW1" dist="LN">
                <imls imt="MMI">0.00 5.00 10.00</imls>
                <meanLRs>0.00  0.5  1.0</meanLRs>
                <covLRs>0.30 0.30 0.30 </covLRs>
            </vulnerabilityFunction>

            <vulnerabilityFunction id="SW2" dist="LN">
                <imls imt="MMI">0.00 5.00 10.00</imls>
                <meanLRs>0.00 0.05  0.1</meanLRs>
                <covLRs>0.30 0.30 0.30 </covLRs>
            </vulnerabilityFunction>
    </vulnerabilityModel>
</nrml>"""

    # Write a file to test
    f = tempfile.NamedTemporaryFile(suffix='.xml',
                                    prefix='building',
                                    delete=False,
                                    mode='w+t')
    f.write(str2)
    f.close()
    return f.name


def build_example_contents_vulnerability():
    """Build an example xml file.
    If you call this remember to delete the file;  os.remove(filename).

    Returns:
        The name of the file
    """
    str2 = """<?xml version='1.0' encoding='utf-8'?>
<nrml xmlns="http://openquake.org/xmlns/nrml/0.5"
      xmlns:gml="http://www.opengis.net/gml">

    <vulnerabilityModel id="EQ_contents"
     assetCategory="not_used"
     lossCategory="contents_loss">
            <vulnerabilityFunction id="RICH" dist="LN">
                <imls imt="MMI">0.00 5.00 10.00</imls>
                <meanLRs>0.00 0.005 0.01</meanLRs>
                <covLRs>0.50 0.50 0.50</covLRs>
            </vulnerabilityFunction>

            <vulnerabilityFunction id="POOR" dist="LN">
                <imls imt="MMI">0.00 5.00 10.00</imls>
                <meanLRs>0.00 0.0005 0.001</meanLRs>
                <covLRs>0.60 0.60 0.60</covLRs>
            </vulnerabilityFunction>
    </vulnerabilityModel>
</nrml>"""

    # Write a file to test
    f = tempfile.NamedTemporaryFile(suffix='.xml',
                                    prefix='contents',
                                    delete=False,
                                    mode='w+t')
    f.write(str2)
    f.close()
    return f.name


def build_example_exposure():
    """Build an example exposure file.
    If you call this remember to delete the file;  os.remove(filename).

    Returns:
        The name of the file
    """
    f = tempfile.NamedTemporaryFile(suffix='.txt',
                                    prefix='test_integration',
                                    delete=False,
                                    mode='w+t')
    f.write('lat, long, building, contents, m2,' +
            'building_costperm2, contents_costperm2, MMI\n')
    f.write('-36., 144., SW1, RICH, 100, 30, 20, 4\n')
    f.write('-36., 145., SW2, POOR, 50, 20, 15, 5\n')
    f.close()

    return f.name, 'lat', 'long'


class TestIntegration(unittest.TestCase):

    """
    Test how all of the modules work in a standard workflow.
    """

    def test_exposure_and_vuln_functions(self):
        # Create the files
        building_vulnerability = build_example_building_vulnerability()
        contents_vulnerability = build_example_contents_vulnerability()
        file_exp, lat_name, long_name = build_example_exposure()

        the_config = [{'template': 'default'},
                      {jobs.LOADCSVEXPOSURE:
                       {'file_name': file_exp,
                        'exposure_latitude': lat_name,
                        'exposure_longitude': long_name}},
                      {jobs.LOADXMLVULNERABILITY: {'file_name': [building_vulnerability, contents_vulnerability]}},
                      {jobs.SIMPLELINKER: {'vul_functions_in_exposure':
                                           {"EQ_building": 'building',
                                            "EQ_contents": 'contents'}}},
                      {jobs.SELECTVULNFUNCTION: {'variability_method':
                                                 {"EQ_building": 'mean',
                                                  "EQ_contents": 'mean'}}},
                      {jobs.LOOKUP: None}]
        context = main.start(config_list=the_config)

        # SW1 loss ratio
        #  SW1 4 MMI - 0.4 building_loss , 0.004 contents_loss
        #  SW2 5 MMI - 0.05 building_loss 0.0005 contents_loss

        if parallel.STATE.size == 1:
            results = [0.4, 0.05]
            actual = context.exposure_att['building_loss']
            self.assertTrue(allclose(actual,
                                     results), 'actual:' + str(actual) +
                            '\n results:' + str(results))
        else:
            if parallel.STATE.rank == 0:
                results = [0.4]
                actual = context.exposure_att['building_loss']
                self.assertTrue(allclose(actual,
                                         results), 'actual:' + str(actual) +
                                '\n results:' + str(results))
            elif parallel.STATE.rank == 1:
                results = [0.05]
                actual = context.exposure_att['building_loss']
                self.assertTrue(allclose(actual,
                                         results), 'actual:' + str(actual) +
                                '\n results:' + str(results))

        os.remove(building_vulnerability)
        os.remove(contents_vulnerability)
        os.remove(file_exp)


# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestIntegration, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

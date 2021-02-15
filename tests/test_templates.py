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
Test templates
"""

import os
import unittest

from hazimp import misc
from hazimp.jobs.jobs import LOADCSVEXPOSURE, LoadCsvExposure, LoadRaster, LoadXmlVulnerability, SimpleLinker, \
    SelectVulnFunction, LookUp, SaveExposure, SaveProvenance, CATEGORISE, PermutateExposure, MultipleDimensionMult, \
    AggregateLoss, SaveAggregation, Categorise, Aggregate, Tabulate
from hazimp.templates import WINDNC, READERS, VULNFILE, PERMUTATION, CALCSTRUCTLOSS, AGGREGATION, SAVE, \
    VULNSET, HAZARDRASTER, AGGREGATE, TABULATE, SAVEAGG


class TestTemplates(unittest.TestCase):
    def setUp(self):
        pass

    def test_template_wind_nc_without_optional_jobs(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            VULNFILE: 'curve.xml',
            VULNSET: 'wind',
            SAVE: 'output.csv'
        }

        jobs = READERS[WINDNC](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (LookUp, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_nc_with_optional_jobs(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            VULNFILE: 'curve.xml',
            VULNSET: 'wind',
            PERMUTATION: {},
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            AGGREGATION: {},
            SAVEAGG: 'aggregation.csv',
            CATEGORISE: {},
            AGGREGATE: {},
            TABULATE: {},
            SAVE: 'output.csv'
        }

        jobs = READERS[WINDNC](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural_loss_ratio',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (Categorise, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (Aggregate, {}),
            (Tabulate, {}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def assertJobs(self, actual: list, expected: list):
        self.assertEqual(len(actual), len(expected))

        for i, (instance, attributes) in enumerate(expected):
            print(instance.__name__)
            self.assertIsInstance(actual[i].job_instance, instance)
            self.assertEqual(actual[i].atts_to_add, attributes)


if __name__ == '__main__':
    unittest.main()

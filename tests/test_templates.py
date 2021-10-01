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
from hazimp.calcs.calcs import FLOOR_HEIGHT, CalcFloorInundation
from hazimp.jobs.jobs import (LOADCSVEXPOSURE, LoadCsvExposure, LoadRaster,
                              LoadXmlVulnerability, SimpleLinker,
                              SelectVulnFunction, LookUp, SaveExposure,
                              SaveProvenance, CATEGORISE,
                              PermutateExposure, MultipleDimensionMult,
                              AggregateLoss, SaveAggregation, Categorise,
                              Aggregate, Tabulate, Const,
                              RandomConst, Add)
from hazimp.templates import (WINDNC, READERS, VULNFILE, PERMUTATION,
                              CALCSTRUCTLOSS, AGGREGATION, SAVE,
                              VULNSET, HAZARDRASTER, AGGREGATE, TABULATE,
                              SAVEAGG, WINDV5, CALCCONTLOSS, FLOODCONTENTSV2,
                              FLOODFABRICV2, WINDV4, WINDV3, EARTHQUAKEV1)
from hazimp.templates.flood import CONT_ACTIONS, INSURE_PROB


class TestTemplates(unittest.TestCase):
    def setUp(self):
        pass

    def test_template_wind_nc_without_optional_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {'file_list': 'hazard.tif'},
            VULNFILE: 'curve.xml',
            VULNSET: 'wind',
            SAVE: 'output.csv'
        }

        jobs = READERS[WINDNC](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': 'hazard.tif'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (LookUp, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_nc_with_optional_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {'file_list': ['hazard.tif']},
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
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': ['hazard.tif']}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (Categorise, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (Aggregate, {'categorise': {}}),
            (Tabulate, {}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_earthquake_v1(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {'file_list': ['hazard.tif']},
            VULNFILE: 'curve.xml',
            VULNSET: 'eq',
            PERMUTATION: {},
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            AGGREGATION: {},
            SAVEAGG: 'aggregation.csv',
            CATEGORISE: {},
            AGGREGATE: {},
            TABULATE: {},
            SAVE: 'output.csv'
        }

        jobs = READERS[EARTHQUAKEV1](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': 'MMI', 'file_list': ['hazard.tif']}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'eq': 'EQ_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'eq': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (Categorise, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (Aggregate, {'categorise': {}}),
            (Tabulate, {}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_earthquake_v1_categorise_aggregate(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {'file_list': 'hazard.tif'},
            VULNFILE: 'curve.xml',
            VULNSET: 'eq',
            PERMUTATION: {},
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            AGGREGATION: {},
            SAVEAGG: 'aggregation.csv',
            CATEGORISE: {'field_name': 'Damage state'},
            AGGREGATE: {'boundaries': 'boundary.geojson'},
            TABULATE: {},
            SAVE: 'output.csv'
        }

        jobs = READERS[EARTHQUAKEV1](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': 'MMI', 'file_list': 'hazard.tif'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'eq': 'EQ_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'eq': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (Categorise, {'field_name': 'Damage state'}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (Aggregate, {'boundaries': 'boundary.geojson', 'categorise': {'field_name': 'Damage state'}}),
            (Tabulate, {}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_nc_fails_without_mandatory(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {'file_list': 'hazard.tif'},
            VULNFILE: 'curve.xml',
            VULNSET: 'wind',
            PERMUTATION: {},
            CALCSTRUCTLOSS: {},
            AGGREGATION: {},
            SAVEAGG: 'aggregation.csv',
            CATEGORISE: {},
            AGGREGATE: {},
            TABULATE: {},
            SAVE: 'output.csv'
        }

        with self.assertRaises(RuntimeError) as context:
            READERS[WINDNC](config)

        self.assertEqual(
            'Mandatory key not found in config file; replacement_value_label',
            str(context.exception)
        )

    def test_template_wind_v5_without_optional_config(self):
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
            SAVE: 'output.csv',
            SAVEAGG: 'aggregation.csv',
        }

        jobs = READERS[WINDV5](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': {}}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_v5_with_optional_config(self):
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
            CATEGORISE: {},
            TABULATE: {},
            SAVE: 'output.csv',
            SAVEAGG: 'aggregation.csv',
        }

        jobs = READERS[WINDV5](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': {}}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (PermutateExposure, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (AggregateLoss, {}),
            (Categorise, {}),
            (Tabulate, {}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveAggregation, {'file_name': 'aggregation.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_v4_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            VULNFILE: 'curve.xml',
            VULNSET: 'wind',
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            SAVE: 'output.csv',
            SAVEAGG: 'aggregation.csv',
        }

        jobs = READERS[WINDV4](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': {}}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'curve.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (LookUp, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_wind_v3_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            VULNSET: 'wind',
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            SAVE: 'output.csv',
            SAVEAGG: 'aggregation.csv',
        }

        jobs = READERS[WINDV3](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'attribute_label': '0.2s gust at 10m height m/s', 'file_list': {}}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'synthetic_domestic_wind_vul_curves.xml')}),
            (SimpleLinker, {'vul_functions_in_exposure': {'wind': 'WIND_VULNERABILITY_FUNCTION_ID'}}),
            (SelectVulnFunction, {'variability_method': {'wind': 'mean'}}),
            (LookUp, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_flood_contents_v2_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            FLOOR_HEIGHT: 0.3,
            CONT_ACTIONS: {
                'save': 0.2,
                'no_action': 0.7,
                'expose': 0.1
            },
            INSURE_PROB: {
                'insured': 0.3,
                'uninsured': 0.7
            },
            CALCCONTLOSS: {
                'replacement_value_label': 'REPLACEMENT_VALUE'
            },
            SAVE: 'output.csv'
        }

        jobs = READERS[FLOODCONTENTSV2](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'file_list': {}, 'attribute_label': 'water_depth'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'content_flood_avg_curve.xml')}),
            (Const, {'var': 'floor_height_(m)', 'value': 0.3}),
            (CalcFloorInundation, {}),
            (RandomConst, {'values': {'_EXPOSE': 0.1, '_NOACTION': 0.7, '_SAVE': 0.2},
                           'var': 'contents_action'}),
            (RandomConst, {'values': {'_INSURED': 0.3, '_UNINSURED': 0.7},
                           'var': 'insurance_regime'}),
            (Add, {'var1': 'BUILDING_TYPE',
                   'var2': 'insurance_regime',
                   'var_out': 'regime_action'}),
            (Add, {'var1': 'regime_action',
                   'var2': 'contents_action',
                   'var_out': 'CONTENTS_FLOOD_FUNCTION_ID'}),
            (SimpleLinker, {'vul_functions_in_exposure':
                            {'contents_domestic_flood_2012': 'CONTENTS_FLOOD_FUNCTION_ID'}
                            }),
            (SelectVulnFunction, {'variability_method': {'contents_domestic_flood_2012': 'mean'}}),
            (LookUp, {}),
            (MultipleDimensionMult, {'var1': 'contents',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'contents_loss'}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def test_template_flood_fabric_v2_config(self):
        config = {
            LOADCSVEXPOSURE: {
                'file_name': 'exposure.csv'
            },
            HAZARDRASTER: {},
            FLOOR_HEIGHT: 0.3,
            CALCSTRUCTLOSS: {'replacement_value_label': 'REPLACEMENT_VALUE'},
            SAVE: 'output.csv'
        }

        jobs = READERS[FLOODFABRICV2](config)

        self.assertJobs(jobs, [
            (LoadCsvExposure, {'file_name': 'exposure.csv'}),
            (LoadRaster, {'file_list': {}, 'attribute_label': 'water_depth'}),
            (LoadXmlVulnerability, {'file_name': os.path.join(misc.RESOURCE_DIR, 'fabric_flood_avg_curve.xml')}),
            (Const, {'var': 'floor_height_(m)', 'value': 0.3}),
            (CalcFloorInundation, {}),
            (SimpleLinker, {'vul_functions_in_exposure':
                            {'structural_domestic_flood_2012': 'FABRIC_FLOOD_FUNCTION_ID'}
                            }),

            (SelectVulnFunction, {'variability_method': {'structural_domestic_flood_2012': 'mean'}}),
            (LookUp, {}),
            (MultipleDimensionMult, {'var1': 'structural',
                                     'var2': 'REPLACEMENT_VALUE',
                                     'var_out': 'structural_loss'}),
            (SaveExposure, {'file_name': 'output.csv'}),
            (SaveProvenance, {'file_name': 'output.xml'})
        ])

    def assertJobs(self, actual: list, expected: list):
        for i, job in enumerate(actual):
            (instance, attributes) = expected[i]
            self.assertIsInstance(job.job_instance, instance)
            self.assertEqual(attributes, job.atts_to_add)


if __name__ == '__main__':
    unittest.main()

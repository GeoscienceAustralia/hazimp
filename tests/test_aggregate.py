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
Test aggregating impact data into a choropleth map
"""
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from pandas._testing import assert_frame_equal

from hazimp.aggregate import (choropleth, aggregate_loss_atts,
                              aggregate_categorisation)
from tests import CWD

outputs_to_test = [
    'output.json',
    'output.geojson',
    'output.shp',
    'output.gpkg'
]


class TestAggregate(unittest.TestCase):
    def setUp(self):
        pass

    def assert_file_exists(self, filename):
        if not Path(filename).resolve().is_file():
            raise AssertionError(f'Expected file to exist: {filename}')

    def test_choropleth_creates_output(self):
        for output in outputs_to_test:
            with self.subTest(output):
                data_frame = pd.read_csv(str(CWD / 'data/exposure_with_loss.csv'))

                temp_dir = tempfile.TemporaryDirectory()
                filename = f'{temp_dir.name}/{output}'

                try:
                    choropleth(
                        data_frame,
                        str(CWD / 'data/boundaries.json'),
                        'MESHBLOCK_CODE_2011',
                        'MB_CODE11',
                        filename,
                        {'structural': ['mean']},
                        True,
                        None
                    )

                    self.assert_file_exists(filename)
                finally:
                    temp_dir.cleanup()

    def test_choropleth_invalid_boundary(self):
        with self.assertRaises(SystemExit) as context:
            data_frame = pd.read_csv(str(CWD / 'data/exposure_with_loss.csv'))

            choropleth(
                data_frame,
                str(CWD / 'data/boundaries.json'),
                'MESHBLOCK_CODE_2011',
                'INVALID',
                'output.json',
                {'structural': ['mean']},
                True,
                None
            )

        self.assertEqual(context.exception.code, 1)

    def test_choropleth_invalid_driver(self):
        data_frame = pd.read_csv(str(CWD / 'data/exposure_with_loss.csv'))

        status = choropleth(
            data_frame,
            str(CWD / 'data/boundaries.json'),
            'MESHBLOCK_CODE_2011',
            'MB_CODE11',
            'output.invalid',
            {'structural': ['mean']},
            True,
            None
        )

        self.assertFalse(status)

    def test_aggregate_loss_atts(self):
        data_frame = pd.DataFrame({'A': ['X', 'Y', 'Y'], 'B': [1, 2, 3]})
        aggregated = aggregate_loss_atts(data_frame, 'A', {'B': 'sum'})

        assert_frame_equal(pd.DataFrame({'A': ['X', 'Y'], 'B': [1, 5]}), aggregated)

    def test_aggregate_loss_atts_invalid_field(self):
        with self.assertRaises(SystemExit) as context:
            data_frame = pd.DataFrame({'A': ['X', 'Y', 'Y'], 'B': [1, 2, 3]})
            aggregate_loss_atts(data_frame, 'Z')

        self.assertEqual(context.exception.code, 1)

    def test_aggregate_categorisation_simple_label(self):
        data_frame = pd.DataFrame({'structural_mean': [0.25]})

        expected_data_frame = data_frame.copy()
        expected_data_frame['Damage state'] = 'Extensive'

        categorise = {
            'field_name': 'Damage state',
            'bins': [0.0, 0.02, 0.1, 0.2, 0.5, 1.0],
            'labels': [
                'Negligible',
                'Slight',
                'Moderate',
                'Extensive',
                'Complete'
            ]
        }

        fields = {
            'structural': ['mean']
        }

        aggregate_categorisation(
            data_frame,
            categorise,
            fields,
            'Damage state'
        )

        assert_frame_equal(expected_data_frame, data_frame)

    def test_aggregate_categorisation_detailed_labels(self):
        data_frame = pd.DataFrame({
            'structural_mean': [0.1],
            'structural_max': [0.2]
        })

        expected_data_frame = data_frame.copy()
        expected_data_frame['Damage state (structural_mean)'] = 'Moderate'
        expected_data_frame['Damage state (structural_max)'] = 'Extensive'

        categorise = {
            'field_name': 'Damage state',
            'bins': [0.0, 0.02, 0.1, 0.2, 0.5, 1.0],
            'labels': [
                'Negligible',
                'Slight',
                'Moderate',
                'Extensive',
                'Complete'
            ]
        }

        fields = {
            'structural': ['mean', 'max']
        }

        aggregate_categorisation(
            data_frame,
            categorise,
            fields,
            'Damage state'
        )

        assert_frame_equal(expected_data_frame, data_frame)


if __name__ == '__main__':
    unittest.main()

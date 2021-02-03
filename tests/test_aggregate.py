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

from hazimp.aggregate import choropleth

cwd = Path(__file__).parent

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
                dframe = pd.read_csv(str(cwd / 'data/exposure_with_loss.csv'))

                temp_dir = tempfile.TemporaryDirectory()
                filename = f'{temp_dir.name}/{output}'

                try:
                    choropleth(
                        dframe,
                        str(cwd / 'data/boundaries.json'),
                        'MESHBLOCK_CODE_2011',
                        'MB_CODE11',
                        filename,
                        True
                    )

                    self.assert_file_exists(filename)
                finally:
                    temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()

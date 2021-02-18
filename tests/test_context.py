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

"""
Test the workflow module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, ANY, call

import numpy
import pandas as pd
from mock import MagicMock
from numpy.testing import assert_array_equal
from pandas._testing import assert_frame_equal
from scipy import allclose, array, arange

from hazimp import context
from hazimp import misc
from hazimp.context import save_csv_agg
from tests import CWD


class TestContext(unittest.TestCase):

    """
    Test the workflow module
    """

    def test_save_exposure_atts(self):

        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.npz',
                                        prefix='test_save_exposure_atts',
                                        delete=False)
        f.close()

        con = context.Context()
        con.set_prov_label('test label')
        actual = {'shoes': array([10., 11]),
                  'depth': array([[5., 3.], [2., 4]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 2.])
        con.exposure_lat = lat
        lon = array([10., 20.])
        con.exposure_long = lon
        con.save_exposure_atts(f.name, use_parallel=False)

        with numpy.load(f.name) as exp_dict:
            actual[context.EX_LONG] = lon
            actual[context.EX_LAT] = lat
            for keyish in exp_dict.files:
                self.assertTrue(allclose(exp_dict[keyish],
                                         actual[keyish]))
        os.remove(f.name)

    def test_get_site_count(self):
        con = context.Context()
        actual = {'shoes': array([10., 11]),
                  'depth': array([[5., 3.], [2., 4]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 2.])
        con.exposure_lat = lat
        lon = array([10., 20.])
        con.exposure_long = lon
        self.assertEqual(con.get_site_shape(), (2,))

    def test_save_exposure_attsII(self):

        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.csv',
                                        prefix='test_save_exposure_atts',
                                        delete=False)
        f.close()
        con = context.Context()
        con.set_prov_label('test label')
        actual = {'shoes': array([10., 11, 12]),
                  'depth': array([[5., 4., 3.], [3., 2, 1], [30., 20, 10]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 2., 3])
        con.exposure_lat = lat
        lon = array([10., 20., 30])
        con.exposure_long = lon
        con.save_exposure_atts(f.name, use_parallel=False)
        exp_dict = misc.csv2dict(f.name)

        actual[context.EX_LONG] = lon
        actual[context.EX_LAT] = lat
        actual['depth'] = array([4, 2, 20])
        for key in exp_dict:
            self.assertTrue(allclose(exp_dict[key],
                                     actual[key]))
        os.remove(f.name)

    def test_clip_exposure(self):

        # These points are in the HazImp notebook.

        lat_long = array([[-23, 110], [-23, 130], [-23, 145],
                          [-30, 110], [-35, 121], [-25, 139], [-30, 145],
                          [-37, 130]])
        num_points = lat_long.shape[0]
        shoes_array = arange(num_points * 2).reshape((-1, 2))
        d3_array = arange(num_points * 2 * 3).reshape((-1, 2, 3))
        id_array = arange(num_points)

        con = context.Context()
        sub_set = (4, 5)
        initial = {'shoes': shoes_array,
                   'd3': d3_array,
                   misc.INTID: id_array}
        con.exposure_att = initial
        con.exposure_lat = lat_long[:, 0]
        con.exposure_long = lat_long[:, 1]

        # After this clip the only points that remain are;
        # [-35, 121] & [-25, 139], indexed as 4 & 5
        con.clip_exposure(min_lat=-36, max_lat=-24,
                          min_long=120, max_long=140)

        actual = {}
        actual[context.EX_LAT] = lat_long[:, 0][sub_set, ...]
        actual[context.EX_LONG] = lat_long[:, 1][sub_set, ...]
        actual['shoes'] = shoes_array[sub_set, ...]
        actual['d3'] = d3_array[sub_set, ...]
        actual[misc.INTID] = id_array[sub_set, ...]

        for key in con.exposure_att:
            self.assertTrue(allclose(con.exposure_att[key],
                                     actual[key]))

    @patch('hazimp.context.aggregate.choropleth')
    @patch('hazimp.context.misc.upload_to_s3_if_applicable')
    def test_save_aggregation_local(self, upload_mock, choropleth_mock):
        boundaries = str(CWD / 'data/boundaries.json')

        con = context.Context()
        con.set_prov_label('test label')
        con.exposure_att = pd.DataFrame(data={'column': [1, 2, 3]})

        con.save_aggregation('aggregation.json', boundaries, 'MESHBLOCK_CODE_2011',
                             'MB_CODE11', True, {'structural_loss_ratio': ['mean']}, False)

        choropleth_mock.assert_called_with(ANY, boundaries, 'MESHBLOCK_CODE_2011', 'MB_CODE11', 'aggregation.json', {'structural_loss_ratio': ['mean']}, True)
        upload_mock.assert_called_once_with('aggregation.json', None, None)

    @patch('hazimp.context.aggregate.choropleth')
    @patch('hazimp.context.misc.upload_to_s3_if_applicable')
    @patch('hazimp.context.misc.create_temp_file_path_for_s3', lambda x: ('temp/aggregation.shp', 'bucket', 'aggregation.shp'))
    def test_save_aggregation_s3(self, upload_mock: MagicMock, choropleth_mock: MagicMock):
        boundaries = str(CWD / 'data/boundaries.json')

        con = context.Context()
        con.set_prov_label('test label')
        con.exposure_att = pd.DataFrame(data={'column': [1, 2, 3]})

        con.save_aggregation('/vsis3/bucket/aggregation.shp', boundaries, 'MESHBLOCK_CODE_2011',
                             'MB_CODE11', True, {'structural_loss_ratio': ['mean']}, False)

        choropleth_mock.assert_called_with(ANY, boundaries, 'MESHBLOCK_CODE_2011', 'MB_CODE11', 'temp/aggregation.shp', {'structural_loss_ratio': ['mean']}, True)
        upload_mock.assert_has_calls([
            call('temp/aggregation.shp', 'bucket', 'aggregation.shp'),
            call('temp/aggregation.dbf', 'bucket', 'aggregation.dbf'),
            call('temp/aggregation.shx', 'bucket', 'aggregation.shx'),
            call('temp/aggregation.prj', 'bucket', 'aggregation.prj'),
            call('temp/aggregation.cpg', 'bucket', 'aggregation.cpg', True)
        ])

    @patch('hazimp.context.aggregate.aggregate_loss_atts')
    def test_aggregate_loss(self, aggregate_loss_atts_mock: MagicMock):
        mock = MagicMock()
        kwargs = MagicMock()

        con = context.Context()
        con.set_prov_label('test label')
        con.exposure_att = mock

        con.aggregate_loss('groupBy', kwargs)

        aggregate_loss_atts_mock.assert_called_once_with(mock, 'groupBy', kwargs)

    def test_categorise(self):
        curve = MagicMock()
        curve.loss_category_type = 'damage_index'

        data_frame = pd.DataFrame(data={'damage_index': [0, 5, 9]})

        con = context.Context()
        con.exposure_vuln_curves = {'domestic_wind_2012': curve}
        con.exposure_att = data_frame

        con.categorise([0, 2.5, 7.5, 10], ['Low', 'Medium', 'High'], 'category')

        self.assertEqual(['Low', 'Medium', 'High'], data_frame['category'].to_list())

    def test_tabulate(self):
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            con = context.Context()
            con.set_prov_label('test label')
            con.exposure_att = pd.DataFrame({
                'YEAR_BUILT': ['1914 - 1946', '1952 - 1961', '1952 - 1961'],
                'DAMAGE_STATE': ['Slight', 'Moderate', 'Moderate']
            })

            con.tabulate(f.name, 'YEAR_BUILT', 'DAMAGE_STATE', 'size')

            actual = pd.read_excel(f.name, engine='openpyxl')

            self.assertEqual(['YEAR_BUILT', 'Moderate', 'Slight'], actual.columns.to_list())
            self.assertEqual(['Total', 2.0, 1.0], actual.loc[2].to_list())

        os.unlink(f.name)

    def test_save_exposure_aggregation_csv(self):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            con = context.Context()
            con.exposure_agg = pd.DataFrame(data={'column': [1, 2, 3]})
            con.save_exposure_aggregation(f.name, use_parallel=False)

            data_frame = pd.read_csv(f.name, index_col=False)

            assert_frame_equal(
                pd.DataFrame(data={'FID': [0, 1, 2], 'column': [1, 2, 3]}),
                data_frame,
            )

        os.unlink(f.name)

    def test_save_exposure_aggregation_npz(self):
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as f:
            con = context.Context()
            con.exposure_agg = pd.DataFrame(data={'column': [1, 2, 3]})
            con.save_exposure_aggregation(f.name, use_parallel=False)

            with numpy.load(f.name) as data:
                assert_array_equal([1, 2, 3], data['column'])

        os.unlink(f.name)

    def test_save_csv_agg(self):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            save_csv_agg(pd.DataFrame(), f.name)

            actual = pd.read_csv(f.name)
            self.assertIsInstance(actual, pd.DataFrame)

        os.unlink(f.name)


# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestContext, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

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

import numpy
import unittest
import tempfile
import os

from scipy import allclose, array, arange

from hazimp import context
from hazimp import misc


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


# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestContext, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

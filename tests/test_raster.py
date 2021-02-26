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
# pylint says;  Passing unexpected keyword argument 'delete' in function call
# I need to pass it though.
# pylint: disable=R0801

"""
Test the raster module.
"""

import os
import tempfile
import unittest

import numpy
from scipy import asarray, allclose, nan

from hazimp.raster import Raster, recalc_max, files_raster_data_at_points


class TestRaster(unittest.TestCase):

    """
    Test the Raster module
    """

    def test1_raster_data_at_points(self):
        # Write a file to test
        # pylint: disable=R0801
        f = tempfile.NamedTemporaryFile(suffix='.aai',
                                        prefix='test_misc',
                                        delete=False,
                                        mode='w+t')
        f.write('ncols 3  \r\n')
        f.write('nrows 2  \r\n')
        f.write('xllcorner +0.  \r\n')
        f.write('yllcorner +8.  \r\n')
        f.write('cellsize 1  \r\n')
        f.write('NODATA_value -9999  \r\n')
        f.write('1 2 -9999  \r\n')
        f.write('4 5 6  ')
        f.close()
        # lon 0 - 3
        # lat 8 - 10

        lon = asarray([0, 0.9, 1.999])
        lat = asarray([9.9, 9.1, 8.9])

        raster = Raster.from_file(f.name)
        data = raster.raster_data_at_points(lon, lat)
        self.assertEqual(raster.ul_x, 0)
        self.assertEqual(raster.ul_y, 10)
        self.assertEqual(raster.x_pixel, 1)
        self.assertEqual(raster.y_pixel, -1)
        self.assertEqual(raster.x_size, 3)
        self.assertEqual(raster.y_size, 2)
        self.assertTrue(allclose(data, asarray([1., 1., 5.])))

        lon = asarray([0.0001, 0.0001, 2.999, 2.999])
        lat = asarray([8.0001, 9.999, 9.999, 8.0001])
        data = raster.raster_data_at_points(lon, lat)
        index_g = numpy.array([0, 1, 3])
        self.assertTrue(allclose(data[index_g],
                                 asarray([4., 1., 6.])))
        self.assertTrue(numpy.isnan(data[2]))

        os.remove(f.name)

    def test2_raster_data_at_points(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.aai',
                                        prefix='test_misc',
                                        delete=False,
                                        mode='w+t')
        f.write('ncols 3   \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner +0.   \r\n')
        f.write('yllcorner +8. \r\n')
        f.write('cellsize 1   \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('1 2 -9999   \r\n')
        f.write('4 5 6')
        f.close()
        # lon 0 - 3
        # lat 8 - 10

        # Just outside the midpoint of all sides
        lon = asarray([-0.0001, 1.5, 3.0001, 1.5])
        lat = asarray([9., 10.00001, 9.0, 7.99999])
        raster = Raster.from_file(f.name)
        data = raster.raster_data_at_points(lon, lat)
        self.assertTrue(numpy.all(numpy.isnan(data)))

        # Inside lower left corner of No data cell

        lon = asarray([2.0001])
        lat = asarray([9.000019])
        raster = Raster.from_file(f.name)
        data = raster.raster_data_at_points(lon, lat)
        self.assertTrue(numpy.all(numpy.isnan(data)))

        os.remove(f.name)

    def test2_files_raster_data_at_points(self):

        files = []
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.aai',
                                        prefix='test_misc',
                                        delete=False,
                                        mode='w+t')
        f.write('ncols 2   \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner 0.0   \r\n')
        f.write('yllcorner 1.0 \r\n')
        f.write('cellsize 1.5   \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('0 0\r\n')
        f.write('0 0\r\n')
        f.close()
        # lon 0 - 3
        # lat 1 - 4
        files.append(f.name)
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.aai',
                                        prefix='test_misc',
                                        delete=False,
                                        mode='w+t')
        f.write('ncols 2   \r\n')
        f.write('nrows 1 \r\n')
        f.write('xllcorner 1.0   \r\n')
        f.write('yllcorner 0.0 \r\n')
        f.write('cellsize 2.0   \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('1 2 \r\n')
        f.close()
        # lon 1 - 5
        # lat 0 - 2
        files.append(f.name)

        # exposure points, and the hazard values
        # index        0  1  2    3    4   5  6  7
        # 0 val        0  n  n    0    n   n  n  n
        # 1 val        n  n  n    1    2   n  n  n
        lon = asarray([1, 4, 0.5, 1.5, 4, -1, 6, +4])
        lat = asarray([3, 3, 0.5, 1.5, 1, +3, 1, -1])

        data, max_extent = files_raster_data_at_points(lon, lat, files)
        actual = numpy.array([[0, nan], [nan, nan], [nan, nan],
                              [0, 1], [nan, 2], [nan, nan],
                              [nan, nan], [nan, nan]])
        numpy.testing.assert_equal(data, actual)

        self.assertEqual(max_extent, [0, 0, 5, 4])

        for a_file in files:
            os.remove(a_file)

    def test3_recalc_max(self):
        max_extent = (0, 0, 0, 0)
        extent = [-10, -20, 20, 40]
        max_extent = recalc_max(max_extent, extent)
        self.assertEqual(max_extent, extent)

        max_extent = (-100, -10, 10, 100)
        extent = [-10, -20, 20, 40]
        max_extent = recalc_max(max_extent, extent)
        self.assertEqual([-100, -20, 20, 100], max_extent)

        old_max_extent = [-100, -100, 100, 100]
        extent = [-10, -20, 20, 40]
        max_extent = recalc_max(old_max_extent, extent)
        self.assertEqual(old_max_extent, max_extent)


if __name__ == "__main__":
    Suite = unittest.makeSuite(TestRaster, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

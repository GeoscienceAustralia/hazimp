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

"""
Manipulate raster data
"""

import numpy
import gdal
from gdalconst import GA_ReadOnly


class Raster(object):

    """
    A simple class to describe a raster.
    """
    # How about using a geotransform list and taking into account the
    # rotation of the raster? e.g.
    # http://geoexamples.blogspot.com.au/2012/01/
    # creating-files-in-ogr-and-gdal-with.html

    # R0902: 27:Raster: Too many instance attributes (8/7)
    # R0913: 34:Raster.__init__: Too many arguments (9/6)
    # pylint: disable=R0902, R0913

    def __init__(self, raster, upper_left_x, upper_left_y,
                 x_pixel, y_pixel, no_data_value, x_size, y_size):
        """

        :param raster: A 2D numeric array of the raster values, North is up.
                       The values are listed in 'English reading order' i.e.
                       left-right and top-down.
        :param upper_left_x: The longitude at the upper left corner of the
                             top left pixel.
        :param upper_left_y: The latitude at the upper left corner of the
                             top left pixel.
        :param x_pixel: w-e pixel resolution. Pixel Width. Horizontal pixel
                        resolution.
        :param y_pixel: n-s pixel resolution. Pixel Height. Vertical pixel
                        resolution. This is negative.
        :param x_size: Number of columns.
        :param y_size: Number of rows.
        :param no_data_value: Values in the raster that represent no data.
        """
        self.raster = raster
        self.ul_x = upper_left_x
        self.ul_y = upper_left_y
        self.x_pixel = x_pixel
        self.y_pixel = y_pixel
        self.no_data_value = no_data_value
        self.x_size = x_size
        self.y_size = y_size

        self.raster = numpy.where(self.raster == self.no_data_value, numpy.NAN,
                               self.raster)

    @classmethod
    def from_file(cls, filename):
        """
        Load a file in a raster file format known to GDAL.
        Note, image must be 'North up'.

        :param filename: The csv file path string.
        :returns: A Raster instance.
        """

        dataset = gdal.Open(filename, GA_ReadOnly)
        if dataset is None:
            raise RuntimeError('Invalid file: %s' % filename)

        # get georeference info
        transform = dataset.GetGeoTransform()
        assert transform[2] == 0.0  # image is "north up"
        assert transform[4] == 0.0  # image is "north up"
        upper_left_x = transform[0]
        x_pixel = transform[1]
        x_size = dataset.RasterXSize

        upper_left_y = transform[3]
        y_pixel = transform[5]
        y_size = dataset.RasterYSize  # This will be a negative value.
        band = dataset.GetRasterBand(1)
        no_data_value = band.GetNoDataValue()
        raster = band.ReadAsArray(0, 0, x_size, y_size)
        instance = cls(raster, upper_left_x, upper_left_y,
                       x_pixel, y_pixel, no_data_value, x_size, y_size)
        return instance

    @classmethod
    def from_array(cls, raster, upper_left_x, upper_left_y,
                   cell_size, no_data_value):
        """
        Convert numeric array of raster data and info to a raster instance.
        The values are listed in 'English reading order' i.e.
        left-right and top-down.

        :param raster: A 2D numeric array of the raster values, North is up.
        :param upper_left_x: The longitude at the upper left corner.
        :param upper_left_y: The latitude at the upper left corner.
        :param cell_size: The cell size.
        :param no_data_value: Values in the raster that represent no data.
        :returns: A Raster instance
        """
        raster = numpy.array(raster, dtype='d', copy=False)
        if not len(raster.shape) == 2:
            msg = ('Bad Raster shape %s' % (str(raster.shape)))
            raise TypeError(msg)

        x_size = raster.shape[1]
        y_size = raster.shape[0]

        x_pixel = cell_size
        y_pixel = -cell_size

        instance = cls(raster, upper_left_x, upper_left_y,
                       x_pixel, y_pixel, no_data_value, x_size, y_size)
        return instance

    def raster_data_at_points(self, lon, lat):
        """
        Get data at lat lon points of the raster.

        :param lon: A 1D array of the longitude of the points.
        :param lat: A 1D array of the latitude of the points.
        :returns: A numpy array, First dimension being the points/sites.
        """

        assert lon.size == lat.size

        values = numpy.empty(lon.size)
        values[:] = numpy.NAN

        # get an index of all the values inside the grid
        # there has to be a better way...
        bad_indexes = set()
        bad_indexes = bad_indexes.union(numpy.where(lon < self.ul_x)[0])
        bad_indexes = bad_indexes.union(
            numpy.where(lon > self.ul_x + self.x_size * self.x_pixel)[0])
        bad_indexes = bad_indexes.union(numpy.where(lat > self.ul_y)[0])
        bad_indexes = bad_indexes.union(
            numpy.where(lat < self.ul_y + self.y_size * self.y_pixel)[0])
        good_indexes = numpy.array(list(set(
            range(lon.size)).difference(bad_indexes)))

        if good_indexes.shape[0] > 0:
            # compute pixel offset
            raw_col_offset = (lon - self.ul_x) / self.x_pixel
            col_offset = numpy.trunc(raw_col_offset).astype(int)
            raw_row_offset = (lat - self.ul_y) / self.y_pixel
            row_offset = numpy.trunc(raw_row_offset).astype(int)

            values[good_indexes] = self.raster[row_offset[good_indexes],
                                               col_offset[good_indexes]]
            # Change NODATA_value to NAN
            values = numpy.where(values == self.no_data_value, numpy.NAN,
                                 values)
        return values

    def extent(self):
        """
        Return the extent, in lats and longs of the raster.

        :returns: min_long, min_lat, max_long, max_lat
        """

        max_lat = self.ul_y
        min_lat = self.ul_y + self.y_pixel * self.y_size
        min_long = self.ul_x
        max_long = self.ul_x + self.x_pixel * self.x_size
        return min_long, min_lat, max_long, max_lat


def files_raster_data_at_points(lon, lat, files):
    """
    Get data at lat lon points, based on a set of files

    :param files: A list of files.
    :param lon: A 1D array of the longitude of the points.
    :param lat: A 1d array of the latitude of the points.
    :returns: reshaped_data, max_extent
      reshaped_data: A numpy array, shape (sites, hazards) or shape (sites),
        for one hazard.
      max_extent: [min_long, min_lat, max_long, max_lat] A rectange covering
        the extents of all of the loaded rasters.
    """

    data = []
    max_extent = None
    for filename in files:
        a_raster = Raster.from_file(filename)
        results = a_raster.raster_data_at_points(lon, lat)
        data.append(results)

        # Working out the maximum extent
        extent = a_raster.extent()
        if max_extent is None:
            max_extent = list(extent)
        else:
            max_extent = recalc_max(max_extent, extent)

    # shape (hazards, sites)
    data = numpy.asarray(data)
    if data.shape[0] == 1:
        # One hazard
        reshaped_data = numpy.reshape(data, (data.shape[1]))
    else:
        reshaped_data = numpy.rollaxis(data, 1)

    return reshaped_data, max_extent


def recalc_max(max_extent, extent):
    """
    Given an extent and a maximum extent modify maximum extent so
    it covers the extent area.

    Both parameters describe a rectangle;
     [min_long, min_lat, max_long, max_lat]

    :param max_extent: A list describing a rectangular area.
    :param extent: A tuple/list describing the area that must be covered
                   by max_extent.
    """
    lim_funct = (min, min, max, max)
    return [lim(max_e, ext) for max_e, ext, lim in zip(max_extent, extent,
                                                       lim_funct)]

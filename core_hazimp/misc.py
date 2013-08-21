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
Functions that haven't found a proper module.
"""
import os
import csv
from collections import defaultdict
import inspect

import numpy
import gdal
from gdalconst import GA_ReadOnly


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resources')
EXAMPLE_DIR = os.path.join(ROOT_DIR, 'examples')
INTID = 'internal_id'


def csv2dict(filename, add_ids=False):
    """
    Read a csv file in and return the information as a dictionary
    where the key is the column names and the values are column arrays.

    :param add_ids: If True add a key, value of ids, from 0 to n
    :param filename: The csv file path string.
    """
    csvfile = open(filename, 'rb')
    reader = csv.DictReader(csvfile)

    file_dict = defaultdict(list)
    for row in reader:
        for key, val in row.iteritems():
            try:
                val = float(val)
            except (ValueError, TypeError):
                try:
                    val = val.strip()
                    if len(val) == 0:
                        #  This is empty.
                        #  Therefore not a value.
                        val = numpy.nan
                except AttributeError:
                    pass
            file_dict[key.strip()].append(val)

    for key in file_dict.keys():
        file_dict[key] = numpy.asarray(file_dict[key])
    # Get a normal dict now, so KeyErrors are thrown.
    plain_dic = dict(file_dict)
    if add_ids:
        # Add internal id info
        array_len = len(plain_dic[plain_dic.keys()[0]])
        plain_dic[INTID] = numpy.arange(array_len)
    return plain_dic


def instanciate_classes(module):
    """
    Create a dictionary of calc names (key) and the calc instance (value).

    :param module: ??
    """
    callable_instances = {}
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[instance.call_funct] = instance
    return callable_instances


def raster_data_at_points(lat, lon, files):
    """
    Get data at lat lon points, based on a set of files

    :param files: A list of files.
    :param lon: A 1D array of the longitude of the points.
    :param lat: A 1d array of the latitude of the points.
    :returns: A numpy array, shape (sites, hazards) or shape (sites),
    for one hazard.
    """
    gdal.AllRegister()
    data = []
    for filename in files:
        results = raster_data_at_points_a_file(lat, lon, filename)
        data.append(results)
    # shape (hazards, sites)
    data = numpy.asarray(data)
    if data.shape[0] == 1:
        # One hazard
        reshaped_data = numpy.reshape(data, (data.shape[1]))
    else:
        reshaped_data = numpy.reshape(data, (-1, data.shape[0]))

    return reshaped_data


# R0914: 63:raster_data_at_points_a_file: Too many local variables (19/15)
def raster_data_at_points_a_file(lon, lat, filename):  # pylint: disable=R0914
    """
    Get data at lat lon points, based on a file.

    :param filename: The csv file path string.
    :param lon: A 1D array of the longitude of the points.
    :param lat: A 1D array of the latitude of the points.
    :returns: A numpy array, First dimension being the points/sites.
    """

    assert lon.size == lat.size

    dataset = gdal.Open(filename, GA_ReadOnly)
    if dataset is None:
        raise RuntimeError('Invalid file: %s' % filename)

    values = numpy.empty(lon.size)
    values[:] = numpy.NAN

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
    data_band = band.ReadAsArray(0, 0, x_size, y_size)

    # get an index of all the values inside the grid
    # there has to be a better way...
    bad_indexes = set()
    bad_indexes = bad_indexes.union(numpy.where(lon < upper_left_x)[0])
    bad_indexes = bad_indexes.union(
        numpy.where(lon > upper_left_x + x_size * x_pixel)[0])
    bad_indexes = bad_indexes.union(numpy.where(lat > upper_left_y)[0])
    bad_indexes = bad_indexes.union(
        numpy.where(lat < upper_left_y + y_size * y_pixel)[0])
    good_indexes = numpy.array(list(set(
        range(lon.size)).difference(bad_indexes)))

    if good_indexes.shape[0] > 0:
        # compute pixel offset
        col_offset = numpy.trunc((lon - upper_left_x) / x_pixel).astype(int)
        row_offset = numpy.trunc((lat - upper_left_y) / y_pixel).astype(int)

        values[good_indexes] = data_band[row_offset[good_indexes],
                                         col_offset[good_indexes]]
        # Change NODATA_value to NAN
        values = numpy.where(values == no_data_value, numpy.NAN, values)

    return values


def get_required_args(func):
    """
    Get the arguments required in a function, from the function.

    :param func: The function that you need to know about.
    """

    #http://stackoverflow.com/questions/196960/
    #can-you-list-the-keyword-arguments-a-python-function-receives

    # *args and **kwargs are not required, so ignore them.
    args_and_defaults, _, _, default_vaules = inspect.getargspec(func)
    defaults = []
    if default_vaules is None:
        args = args_and_defaults
    else:
        args = args_and_defaults[:-len(default_vaules)]
        defaults = args_and_defaults[-len(default_vaules):]
    return args, defaults


def squash_narray(ary):
    """
    Reduce an array to 1 dimension. Firstly try to average the values.
    If that doesn't work only take the first dimension.

    :param ary: the numpy array to be squashed.
    :returns: The ary array, averaged to 1d.
    """
    if ary.ndim > 1:
        try:
            d1_ary = ary.reshape((ary.shape[0], -1)).mean(axis=1)
        except TypeError:
            # Can't average, just take the first axis
            d1_ary = ary.reshape((ary.shape[0], -1))[:, 0]
    else:
        d1_ary = ary
    return d1_ary

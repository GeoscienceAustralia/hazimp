# -*- coding: utf-8 -*-


"""
Functions that haven't found a proper module.
"""
import csv
from collections import defaultdict
import inspect

import gdal
from gdalconst import GA_ReadOnly
import numpy
import os


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resources')
        
def csv2dict(filename):
    """
    Read a csv file in and return the information as a dictionary 
    where the key is the column names and the values are column arrays.
    """
    csvfile = open(filename, 'rb')
    reader = csv.DictReader(csvfile)

    file_dict = defaultdict(list)
    for row in reader:
        for key, val in row.iteritems():
            try:
                val = float(val)
            except ValueError:
                try:
                    val = val.strip()
                except AttributeError:
                    pass
            file_dict[key.strip()].append(val)
    return file_dict

    
def instanciate_classes(module):
    """
    Create a dictionary of calculation names (key) and the calc instance (value)
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
    """
    gdal.AllRegister()
    data = []
    for filename in files:
        results = raster_data_at_points_a_file(lat, lon, filename)
        data.append(results)
    return numpy.asarray(data)
    
       
def raster_data_at_points_a_file(lon, lat, filename):# pylint: disable=R0914
    """
    Get data at lat lon points, based on a file.
    
    lon, lat must be 1D arrays
    """
    # R0914: 63:raster_data_at_points_a_file: Too many local variables (19/15)
    
    
    assert lon.size == lat.size
    
    dataset = gdal.Open(filename, GA_ReadOnly)
    if dataset is None:
        raise RuntimeError('Invalid file: %s' % filename)

    values = numpy.empty(lon.size)
    values[:] = numpy.NAN
    
    # get georeference info
    transform = dataset.GetGeoTransform()
    upper_left_x = transform[0]
    x_pixel = transform[1]
    x_size = dataset.RasterXSize
    
    upper_left_y = transform[3]
    y_pixel = transform[5]
    y_size = dataset.RasterYSize
    band = dataset.GetRasterBand(1)  
    no_data_value =  band.GetNoDataValue() 
    data_band = band.ReadAsArray(0, 0, x_size, y_size)
    
    # get an index of all the values inside the grid
    # there has to be a better way...
    bad_indexes = set()
    bad_indexes = bad_indexes.union(numpy.where(lon < upper_left_x)[0])
    bad_indexes = bad_indexes.union(
        numpy.where(lon > upper_left_x + x_size *  x_pixel)[0]) 
    bad_indexes = bad_indexes.union(numpy.where(lat > upper_left_y)[0])
    bad_indexes = bad_indexes.union(
        numpy.where(lat < upper_left_y + y_size *  y_pixel)[0])
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
    

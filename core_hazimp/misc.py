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
    
       
def raster_data_at_points_a_file(lon, lat, filename):
    """
    Get data at lat lon points, based on a file.
    """
    dataset = gdal.Open(filename, GA_ReadOnly)
    if dataset is None:
        raise RuntimeError('Invalid file: %s' % filename)

    # get georeference info
    transform = dataset.GetGeoTransform()
    x_origin = transform[0]
    y_origin = transform[3]
    pixel_width = transform[1]
    pixel_height = transform[5]
    
    band = dataset.GetRasterBand(1) 
    
    data_band = band.ReadAsArray(0, 0,
                                 dataset.RasterXSize,
                                 dataset.RasterYSize)
    
    
    # compute pixel offset
    x_offset = numpy.trunc((lon - x_origin) / pixel_width).astype(int)
    y_offset = numpy.trunc((lat - y_origin) / pixel_height).astype(int)
    data = data_band[x_offset, y_offset]
    return data

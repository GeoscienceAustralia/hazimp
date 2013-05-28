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
EXAMPLE_DIR = os.path.join(ROOT_DIR, 'examples')
        
def csv2dict(filename):
    """
    Read a csv file in and return the information as a dictionary 
    where the key is the column names and the values are column arrays.
    
    Args:
        filename: The csv file path string.
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
                except AttributeError:
                    pass
            file_dict[key.strip()].append(val)
    # Get a normal dict now, so KeyErrors are thrown.        
    plain_dic =  dict(file_dict)
    return plain_dic
    

    
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
    
    Args:
        filename: The csv file path string.
        lon: A 1D array of the longitude of the points.
        lat: A 1d array of the latitude of the points.
        
    Returns:
        A numpy array, shape (sites, hazards) or shape (sites), for one hazard. 
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
    
       
def raster_data_at_points_a_file(lon, lat, filename):# pylint: disable=R0914
    """
    Get data at lat lon points, based on a file.
    
    Args:
        filename: The csv file path string.
        lon: A 1D array of the longitude of the points.
        lat: A 1d array of the latitude of the points.
        
    Returns:
        A numpy array, First dimension being the points/sites.    
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
    
    
         
def dict2csv(data_dict, filename):
    """
    Write a csv file where the key is the column names and the values
    are numpy arrays.  If the arrays have 2 dimensions the
    other dimension is averaged so there is only 1 dimension.
    
    3 or more dimensions cause an error.
    
    Args:
        filename: The csv file to be written.
        data_dict: The dictionary with the data
         
    """
    
    header = []
    columns = []
    for key, val in data_dict.iteritems():
        header.append(key)
        if len(val.shape) == 2:
            val = numpy.average(val, axis=1)
        elif len(val.shape) > 2:
            msg = 'Too many dimensions in exposure_att %s' % key
            raise RuntimeError(msg)    
        columns.append(val)
    output = numpy.column_stack(tuple(columns))
    fid = open( filename, 'w' ) 
    fid.write(",".join(header) + '\n') 
    numpy.savetxt(fid, output, delimiter=',')
    fid.close() 
    
def save_data(context, filename):
    """
    Write a npz file which has all the exposure arrays.
    
    Args:
        filename: The csv file to be written.
        context: The context object.         
    """
    context.save_exposure_atts(filename)
    

def get_required_args(func):
    """
    Get the arguments required in a function
    
    http://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-python-function-receives
    """
    # *args and **kwargs are not required, so ignore them.
    args_and_defaults, _, _, default_vaules = inspect.getargspec(func)
    defaults = []
    if default_vaules is None:
        args = args_and_defaults
    else:
        args = args_and_defaults[:-len(default_vaules)]
        defaults = args_and_defaults[-len(default_vaules):]
    return args, defaults
          

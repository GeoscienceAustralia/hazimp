
        # -*- coding: utf-8 -*-

"""
A collection of jobs to put into the pipeline.
Jobs know about the context instance.
The
initial jobs will be for setting up the calculations, such as loading
the exposure data.

And key, value pairs that are in the config file are passed to the
jobs function.  The function name is used to determine what to pass in.

"""

import inspect
import sys

from core_hazimp.misc import csv2dict
from core_hazimp.misc import instanciate_classes


class Job(object):
    """
    Abstract Jobs class. Should use abc then.
    """
    def __init__(self):
        """
        Initalise a Calculator object having the attributes
        allargspec_call and args_in.
        """
        self.call_funct = None
                  
        
    def get_call_funct(self):
        """
        Return the 'user' name for the function
        """
        return self.call_funct
        
        
class ConstTest(Job):
    """
    Simple test class. Moving a config value to the context.
    """
    def __init__(self):
        super(ConstTest, self).__init__()
        self.call_funct = 'const_test'


    def __call__(self, context, c_test=None):
        """
        A dummy job for testing.
        """
        context.exposure_att['c_test'] = c_test 

def load_csv_exposure(context, exposure_file=None, exposure_lat=None,
                      exposure_long=None):
    """
    Read a csv exposure file into the context object.
    
    
    Args:
       context: The context instance, used to move data around.
    """
    file_dict = csv2dict(exposure_file)
    
    # FIXME Need to do better error handling
    
    if exposure_lat == None:
        lat_key = EX_LAT
    else:
        lat_key = exposure_lat
    
    try:
        context.exposure_lat = file_dict[lat_key]
    except KeyError:
        pass
    
    if exposure_lat == None:
        long_key = EX_LONG
    else:
        long_key = exposure_long
    
    try:
        context.exposure_long = file_dict[long_key]
    except KeyError:
        pass
    
     
JOBS = instanciate_classes(sys.modules[__name__])

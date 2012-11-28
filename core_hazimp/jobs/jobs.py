
        # -*- coding: utf-8 -*-

"""
A collection of jobs to put into the pipeline.
Jobs know about the context instance.

Config handling needs to be sorted out.
"""

import inspect
import sys

from core_hazimp.misc import csv2dict
from core_hazimp.misc import instanciate_classes

"""
Jobs are a processing unit that know about the context object.  The
initial jobs will be for setting up the calculations, such as loading
the exposure data.
"""

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

def load_csv_exposure(context, config):
    """
    Read a csv exposure file into the context object.
    
    
    Args:
       context: The context instance, used to move data around.
    """
    
    pass
    
     
JOBS = instanciate_classes(sys.modules[__name__])

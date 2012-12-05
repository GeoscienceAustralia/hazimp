
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

import sys 
from scipy import asarray

from core_hazimp.misc import csv2dict
from core_hazimp.workflow import  EX_LAT, EX_LONG
from core_hazimp.misc import instanciate_classes
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file


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

class LoadCsvExposure(Job):
    """
    Read a csv exposure file into the context object.
    """
    def __init__(self):
        super(LoadCsvExposure, self).__init__()
        self.call_funct = 'load_csv_exposure'


    def __call__(self, context, exposure_file=None, exposure_lat=None,
                      exposure_long=None):
        """
        Read a csv exposure file into the context object.     
        
        Args:
            context: The context instance, used to move data around.
            exposure_file: The csv file to load.
            exposure_lat: the title string of the latitude column.
            exposure_long: the title string of the longitude column.
        """
    
        file_dict = csv2dict(exposure_file)
    
        # FIXME Need to do better error handling
    
        if exposure_lat == None:
            lat_key = EX_LAT
        else:
            lat_key = exposure_lat
    
        try:
            context.exposure_lat = asarray(file_dict[lat_key])
            del file_dict[lat_key]
        except KeyError:
            pass
    
        if exposure_lat == None:
            long_key = EX_LONG
        else:
            long_key = exposure_long
    
        try:
            context.exposure_long = asarray(file_dict[long_key])
            del file_dict[long_key]
        except KeyError:
            pass
        
        for key in file_dict:
            context.exposure_att[key] = asarray(file_dict[key])
        #try:
         #   context.exposure_att[key] = asarray(file_dict[key])
        #context.exposure_att.update(file_dict)
    

class LoadXmlVulnerability(Job):
    """
    Read the vulnerability sets into the context object.
    """
    def __init__(self):
        super(LoadXmlVulnerability, self).__init__()
        self.call_funct = 'load_xml_vulnerability'


    def __call__(self, context, vulnerability_file=None):
        """
        Read a csv exposure file into the context object.     
        
        Args:
            vulnerability_file: The xml file to load.
        """
        if vulnerability_file is not None:
            vuln_sets = vuln_sets_from_xml_file(vulnerability_file)
            context.vulnerability_sets.update(vuln_sets)
  
class SimpleLinker(Job):
    """
    Link a list of vulnerability functions to each asset, given the
    vulnerability_sets and exposure columns that represents the
    vulnerability function id.
    """
    def __init__(self):
        super(SimpleLinker, self).__init__()
        self.call_funct = 'simple_linker'


    def __call__(self, context, vulnerability_set_function_id=None):
        """
        Link a list of vulnerability functions to each asset, given the
        vulnerability_sets and exposure columns that represents the
        vulnerability function id.    
        
        Args:
            vulnerability_set_function_id: A dictionary with values being
               vulnerability_sets and values being the exposure title that 
               holds vulnerability function ID's.
        """
        for key in vulnerability_set_function_id:
            vuln_set = context.vulnerability_sets[key]
            
                                 
JOBS = instanciate_classes(sys.modules[__name__])

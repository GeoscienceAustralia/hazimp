
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

from core_hazimp.misc import csv2dict, raster_data_at_points
from core_hazimp.workflow import  EX_LAT, EX_LONG
from core_hazimp.misc import instanciate_classes
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file

LOADCSVEXPOSURE = 'load_csv_exposure'
LOADXMLVULNERABILITY = 'load_xml_vulnerability'
SIMPLELINKER = 'simple_linker'
SELECTVULNFUNCTION  = 'select_vulnerability_functions'
LOOKUP = 'look_up'
LOADRASTER = 'load_raster'


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
        self.call_funct = LOADCSVEXPOSURE


    def __call__(self, context, exposure_file=None, exposure_latitude=None,
                      exposure_longitude=None):
        """
        Read a csv exposure file into the context object.     
        
        Args:
            context: The context instance, used to move data around.
            exposure_file: The csv file to load.
            exposure_latitude: the title string of the latitude column.
            exposure_longitud: the title string of the longitude column.
            
        Content return: 
            exposure_att: Add the file values into this dictionary.
                key: column titles 
                value: column values, except the title
        """
    
        file_dict = csv2dict(exposure_file)
    
        # FIXME Need to do better error handling
    
        if exposure_latitude == None:
            lat_key = EX_LAT
        else:
            lat_key = exposure_latitude
    
        try:
            context.exposure_lat = asarray(file_dict[lat_key])
            del file_dict[lat_key]
        except KeyError:
            pass
    
        if exposure_latitude == None:
            long_key = EX_LONG
        else:
            long_key = exposure_longitude
    
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
        self.call_funct = LOADXMLVULNERABILITY


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
        self.call_funct = SIMPLELINKER


    def __call__(self, context, vul_functions_in_exposure=None):
        """
        Link a list of vulnerability functions to each asset, given the
        vulnerability_sets and exposure columns that represents the
        vulnerability function id.    
        
        Args:
            vul_functions_in_exposure: A dictionary with keys being
               vulnerability_set_ids and values being the exposure title that 
               holds vulnerability function ID's.
               
        Content return:
           vul_function_titles: Add's the exposure_titles
        """
        context.vul_function_titles.update(vul_functions_in_exposure)
        
        
class SelectVulnFunction(Job):
    """
    Produce vulnerability curves for each asset, given the
    vulnerability_sets and exposure columns that represents the
    vulnerability function id.
    
    From the vulnerability set and a function id you get the 
    vulnerability function.  
    Then, using the variability_method e.g. 'mean' you get the
    vulnerability curve.
    """
    def __init__(self):
        super(SelectVulnFunction, self).__init__()
        self.call_funct = SELECTVULNFUNCTION


    def __call__(self, context, variability_method=None):
        """
        Specifies what vulnerability sets to use.
        Links vulnerability curves to assets.
        Assumes the necessary vulnerability_sets have been loaded and
        there is an  exposure column that represents the
        vulnerability function id.
        
        NOTE: This is where the vulnerability function is selected,
            As well as sampled.
        
        Args:
            variability_method: A dictionary with keys being
               vulnerability_set_ids and values being the sampling method
               to generate a vulnerability curve from a vulnerability function.
               e.g. {'EQ_contents': 'mean', 'EQ_building': 'mean'}

        Content return: 
           exposure_vuln_curves: A dictionary of realised
               vulnerability curves, associated with the exposure
               data.
                key - intensity measure
                value - realised vulnerability curve instance per asset
        """
        exposure_vuln_curves = {}
        for vuln_set_key in variability_method:
            # Get the vulnerability set
            vuln_set = context.vulnerability_sets[vuln_set_key]
            # Get the column of function ID's
            exposure_title = context.vul_function_titles[vuln_set_key]
            vuln_function_ids = context.exposure_att[exposure_title]
            # sample from the function to get the curve
            realised_vuln_curves = vuln_set.build_realised_vuln_curves(
                vuln_function_ids,
                variability_method=variability_method[vuln_set_key])
            # Build a dictionary of realised vulnerability curves
            exposure_vuln_curves[vuln_set_key] = realised_vuln_curves
        
        context.exposure_vuln_curves = exposure_vuln_curves
            

class LookUp(Job):
    """
    Do a lookup on all the vulnerability curves, returning the
        associated loss.
    """
    def __init__(self):
        super(LookUp, self).__init__()
        self.call_funct = LOOKUP


    def __call__(self, context):
        """
        Does a look up on all the vulnerability curves, returning the
        associated loss.
               
        Content return: 
           exposure_vuln_curves: A dictionary of realised
               vulnerability curves, associated with the exposure
               data.
                key - intensity measure
                value - realised vulnerability curve instance per asset
        """
        for intensity_key in context.exposure_vuln_curves:
            vuln_curve = context.exposure_vuln_curves[intensity_key]
            int_measure = vuln_curve.intensity_measure_type
            loss_category_type = vuln_curve.loss_category_type
            try:
                intensities = context.exposure_att[int_measure]
            except KeyError:
                vulnerability_set_id = vuln_curve.vulnerability_set_id
                msg = 'Invalid intensity measure, %s. \n' % int_measure
                msg += 'vulnerability_set_id is %s. \n' % vulnerability_set_id
                raise RuntimeError(msg)
            losses = vuln_curve.look_up(intensities)
            context.exposure_att[loss_category_type] = losses
                                         
class LoadRaster(Job):
    """
    Load one or more files and get the value for all the 
    exposure points. Primarily this will be used to load hazard data.
    
    There may be NAN values in this data
    """
    def __init__(self):
        super(LoadRaster, self).__init__()
        self.call_funct = LOADRASTER

    def __call__(self, context, file_list=None, attribute_label=None):
        """
        Load one or more files and get the value for all the 
        exposure points. All files have to be of the same attribute.
             
        Args:
           attribute_label: The string to be associated with this data.
           file_list: A list of files to be loaded.
             
        Content return: 
           exposure_att: Add the file values into this dictionary.
               key: column titles
               value: column values, except the title
        """
        #FIXME raise errors, re no lat or lon
        
        if file_list is not None:
            file_data = raster_data_at_points(context.exposure_long, 
                                              context.exposure_lat, file_list)
            context.exposure_att[attribute_label] = file_data

            
    
#____________________________________________________
#---------------------------------------------------- 
#                KEEP THIS AT THE END
#____________________________________________________   
    
JOBS = instanciate_classes(sys.modules[__name__])

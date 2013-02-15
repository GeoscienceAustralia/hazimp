# -*- coding: utf-8 -*-


"""
Functions concerning the configuration file.
"""

import os
import yaml

from core_hazimp.calcs.calcs import CALCS
from core_hazimp.jobs.jobs import JOBS, LOADRASTER, LOADCSVEXPOSURE, \
    LOADXMLVULNERABILITY, SIMPLELINKER, SELECTVULNFUNCTION, \
    LOOKUP, SAVEALL
from core_hazimp.calcs.calcs import STRUCT_LOSS          
from core_hazimp import misc

DEFAULT = 'default'
LOADWINDTCRM = 'load_wind_tcrm_ascii'
TEMPLATE = 'template'
WINDV1 = 'windv1'

def read_file(file_name):
    """
    Read the configuration file and return the info as a dictionary.
    
    args:
        config_file_name
        
    return:
        A dictionary of the configuration file
    """
    config_file_handle = open(file_name, 'r')
    config_dic = yaml.load(config_file_handle)
        
    return config_dic    

def template_builder(config_dic):
    """
    From the configuration dictionary build and knowing
    the template, build the the job list
    and add predefined info to the config_dic.
    
    args:
        config_dic: A dictionary describing the simulation.
        
    return:
        A list of jobs to process over.
        ** The config_dic isn't returned, but it is modified. 
    """
    
    
    try:
        template = config_dic[TEMPLATE]
    except KeyError:
        template = DEFAULT   
        
    try:    
        reader_function = READERS[str(template)]
    except KeyError:
        raise RuntimeError(
            'Invalid version number, %s in config file.' % version)
            
    jobs = reader_function(config_dic)
    return jobs 

def _reader1(config_dic):
    """
    From a version 1 configuration dictionary build the job list.
    
    args:
        config_dic: A dictionary describing the simulation.
        
    return:
        A list of jobs to process over.   
    """
    
    try:
        job_names = config_dic['jobs']    
    except KeyError:
        raise RuntimeError(
            'No jobs label in config file.')
            
    return get_job_or_calcs(job_names)
    
def _wind_v1_reader(config_dic):
    """
    From a wind v1 configuration dictionary build the job list.
    
    args:
        config_dic: A dictionary describing the simulation.
        
    return:
        A list of jobs to process over.   
    """
    job_names = [LOADCSVEXPOSURE, LOADRASTER, LOADXMLVULNERABILITY,
            SIMPLELINKER, SELECTVULNFUNCTION, LOOKUP, STRUCT_LOSS,
            SAVEALL]
    vul_filename = os.path.join(misc.RESOURCE_DIR, 
                                'domestic_wind_vul_curves.xml')
    file_list = config_dic[LOADWINDTCRM]['file_list']
    config_dic[LOADRASTER] = {'file_list':file_list,
                              'attribute_label':'0.2s gust at 10m height m/s'}
    config_dic[LOADXMLVULNERABILITY] = {'vulnerability_file':vul_filename}
    config_dic[SIMPLELINKER] = {'vul_functions_in_exposure':{
                    'domestic_wind_2012':'wind_vulnerability_model'}}
    config_dic[SELECTVULNFUNCTION] = {'variability_method':{
                    'domestic_wind_2012':'mean'}}
    return get_job_or_calcs(job_names)
    
def get_job_or_calcs(job_names):
    """
    Given a list of job or calc names, return a list of job or calc instances.
    
    arg:
        name: The name if a job or calc.
      
    return:
        A list of Job or Calc instances.
    """
    jobs = []    
    for job_name in job_names:
        jobs.append(get_job_or_calc(job_name))
        
    return jobs

    
def get_job_or_calc(name):
    """
    Given a job or calc name, return the job or calc.
    
    arg:
        name: The name if a job or calc.
      
    return:
        The Job or Calc instance.
    """
    try:
        job = CALCS[name]
    except KeyError:
        try:
            job = JOBS[name]
        except KeyError:
            raise RuntimeError(
            'Invalid job name, %s in config file.' % name)
    return job

READERS = {DEFAULT:_reader1,
           WINDV1:_wind_v1_reader}

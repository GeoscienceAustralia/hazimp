# -*- coding: utf-8 -*-


"""
Functions concerning the configuration file.
"""

import os
import yaml

from core_hazimp.calcs.calcs import CALCS
from core_hazimp.jobs.jobs import JOBS, LOADRASTER, LOADCSVEXPOSURE, \
    LOADXMLVULNERABILITY, SIMPLELINKER, SELECTVULNFUNCTION, \
    LOOKUP, SAVEALL, JOBSKEY
from core_hazimp.calcs.calcs import STRUCT_LOSS          
from core_hazimp import misc

DEFAULT = 'default'
LOADWINDTCRM = 'load_wind_tcrm_ascii'
TEMPLATE = 'template'
WINDV1 = 'windv1'
SAVE = 'save'



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
            'Invalid template name, %s in config file.' % template)
            
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
        job_names = config_dic[JOBSKEY]    
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
    config_dic[LOADRASTER] = {
        'file_list':config_dic[LOADWINDTCRM],
        'attribute_label':'0.2s gust at 10m height m/s'}
    config_dic[LOADXMLVULNERABILITY] = {
        'file_name':vul_filename}
    config_dic[SIMPLELINKER] = {'vul_functions_in_exposure':{
            'domestic_wind_2012':'wind_vulnerability_model'}}
    config_dic[SELECTVULNFUNCTION] = {'variability_method':{
            'domestic_wind_2012':'mean'}}
    config_dic[SAVEALL] = {'file_name':config_dic[SAVE]}
    return get_job_or_calcs(job_names)
 
    
def get_job_or_calcs(job_names):
    """
    Given a list of job or calc names, return a list of job or calc
    instances.
    
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

    
def validate_config(config_dic):
    """
    Check the config_dic
    
    """
    check_files_to_load(config_dic)
    
    
def file_can_open(file2load):
    """
    Check if a file can be opened.
    If it can return True.
    """
    try:
        with open(file2load) as _: 
            pass
    except IOError:
        return False
    return True
    
    
def check_files_to_load(config_dic):
    """
    Check the context, based on the config file.
    
    This function relies on some assumptions.
    All jobs/calcs that load files label the files as;
       file_name OR
       file_list - for a list of files
    """
    bad_files = []
    for value in config_dic.values():
        if isinstance(value, dict):
            if 'file_name' in value:
                file2load = value['file_name']
                if not file_can_open(file2load):
                    bad_files.append(file2load)
            elif 'file_list' in value:
                files2load = value['file_list']
                for file2load in files2load:
                    if not file_can_open(file2load):
                        bad_files.append(file2load)
    if len(bad_files) == 1:        
        raise RuntimeError(
            'Invalid file name, %s in config file.' % bad_files[0])
    elif len(bad_files) > 1:
        raise RuntimeError(
            'Invalid files in config file;\n %s ' % bad_files)
        

READERS = {DEFAULT:_reader1,
           WINDV1:_wind_v1_reader}
           

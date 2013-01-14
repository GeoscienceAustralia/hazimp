# -*- coding: utf-8 -*-


"""
Functions concerning the configuration file.
"""

import yaml

from core_hazimp.calcs.calcs import CALCS
from core_hazimp.jobs.jobs import JOBS


DEFAULT = 1

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
   
def job_reader(config_dic):
    """
    From the configuration dictionary build the job list.
    
    args:
        config_dic: A dictionary describing the simulation.
        
    return:
        A list of jobs to process over.
    """
    
    try:
        version = config_dic['version']
    except KeyError:
        version = DEFAULT   
        
    try:    
        reader_function = READERS[version]
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
    jobs = []
    for job_name in job_names:
        jobs.append(get_job_or_calc(job_name))
        
    return jobs
    
def get_job_or_calc(name):
    """
    Given a job or calc name, return the job or calc.
    
    arg:
        name: The name if a job or calc.
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

READERS = {1:_reader1}

# -*- coding: utf-8 -*-

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

from core_hazimp.pipeline import PipeLineBuilder, PipeLine

class ConfigAwarePipeLine(PipeLine):

    def run(self, context, config):
        """
        
        Run all the jobs in queue, where each job take input data and
        write the results of calculation in context.
        
        Args:
            context: A Context object holding the i/o data for the pipelines
            config: A dictionary of the config info.    
        """

        for job in self.jobs:
            job_kwargs = self.get_job_atts(job, config)
            job(context, **job_kwargs)
            
    def get_job_atts(self, job, config):
        """
        
        Check if any attributes from the config file should be passed
        into the job function. If a key in the config has the same
        name as the job function pass the value, which must be a
        dictionary is returned.
        
        Args:
            config: A dictionary of the config info.    
        
        Returns:
            A dictionary to be passed in the job function as a parameter
        """
        key = job.get_call_funct()
        try:
            # Assuming a Calculator instance
            key = job.get_call_funct()
        except:
            # Assuming it is a function
            key = job._name_
            
        if key in config:
            job_kwargs = config[key]
            # FIXME check that the value is a dictionary
        else:
            job_kwargs = {}
            
        return job_kwargs

class ExposureAttsBuilder(PipeLineBuilder):
    """
    Builds a calc pipeline for jobs that rely on an intermedary function
    to deal with the context instance, which holds are the data. So the
    jobs don't know about the context object.
    
    """
    
    def build(self, calcs):
        """Builds the pipeline.
        
        Args:
           calcs: A list of Calculator instances
        
        Returns:
            A pipeline with the calcs in it, ready to process.
        """
        pipeline = ConfigAwarePipeLine(calcs)
        return pipeline
         

class Context(object):
    """
    Context allows to read the config file
    and store preprocessing/processing steps
    intermediate results.
    """

    def __init__(self):
    
        # Latitude and longitude values of the exposure data
        self.exposure_lat = None
        self.exposure_long = None
        
        # The exposure data at the lats and longs
        self.exposure_att = {}


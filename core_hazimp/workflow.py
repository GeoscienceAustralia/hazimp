# -*- coding: utf-8 -*-

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

from core_hazimp.pipeline import PipeLineBuilder, PipeLine


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
        pipeline = PipeLine(calcs)
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


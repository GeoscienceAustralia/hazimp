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
        pipeline = ExposureAttsPipeLine(calcs)
        return pipeline
         

class ExposureAttsPipeLine(PipeLine):
    """
    Execute the pipeline functions in order, getting input
    from and putting output in context.exposure_att.
    """
    def run(self, context):
        
        """
        Run all the jobs in queue.
        Handling the context here
        
        Args:
            context: A Context instance with values to calculate on.
        """
        for job in self.jobs:
            args_in = []
            for job_arg in job.args_in:
                if not context.exposure_att.has_key(job_arg):
                    #FIXME add warning
                    print "NO CORRECT VARIABLES" 
                    import sys 
                    sys.exit() 
                else:
                    args_in.append(context.exposure_att[job_arg])
            args_out = job(*args_in)
            assert len(args_out) == len(job.args_out)
            for i, arg_out in enumerate(job.args_out):
                context.exposure_att[arg_out] = args_out[i]


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



class ContextBuilder(PipeLineBuilder):
    """
    Builds a pipeline for jobs that directly manipulate the context instance.
    """
    
    def build(self, jobs):
        """Builds the pipeline.
        
        Args:
           jobs: A list of job functions?
        
        Returns:
            A pipeline with the jobs in it, ready to process.
        """
        pipeline = ContextPipeLine(jobs)
        return pipeline
         

class ContextPipeLine(PipeLine):
    """
    Execute the pipeline jobs in order, passing the context
    to each job.
    """
    def run(self, context):
        
        """
        Run all the jobs in queue.
        
        Args:
            context: A Context instance.
        """
        for job in self.jobs:
            args_in = []
            for job_arg in job.args_in:
                if not context.exposure_att.has_key(job_arg):
                    #FIXME add warning
                    print "NO CORRECT VARIABLES" 
                    import sys 
                    sys.exit() 
                else:
                    args_in.append(context.exposure_att[job_arg])
            args_out = job(*args_in)
            assert len(args_out) == len(job.args_out)
            for i, arg_out in enumerate(job.args_out):
                context.exposure_att[arg_out] = args_out[i]

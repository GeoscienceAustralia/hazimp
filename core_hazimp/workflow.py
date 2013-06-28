# -*- coding: utf-8 -*-

# pylint: disable=W0221
# I'm ok with .run having more arg's

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""
import numpy

from core_hazimp.pipeline import PipeLineBuilder, PipeLine

# The standard string names in the context instance
EX_LAT = 'exposure_latitude'
EX_LONG = 'exposure_longitude'


def get_job_atts(job, config):
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

    if key in config:
        job_kwargs = config[key]
        # FIXME check that the value is a dictionary
    else:
        job_kwargs = {}
    return job_kwargs


class ConfigAwarePipeLine(PipeLine):
    """Pipe line that knows passing info in the config dict to the jobs.
    """

    def run(self, context, config):
        """
        Run all the jobs in queue, where each job take input data and
        write the results of calculation in context.

        Args:
            context: A Context object holding the i/o data for the pipelines
            config: A dictionary of the config info.
        """

        for job in self.jobs:
            job_kwargs = get_job_atts(job, config)
            job(context, **job_kwargs)


class ConfigPipeLineBuilder(PipeLineBuilder):
    """
    Builds a pipeline for jobs and calcs.

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
        # key - data name
        # value - A numpy array. First dimension is site.
        self.exposure_att = {}

        # for example 'vulnerability_functions' is a list of a list of
        # vulnerabilty functions.  The outer list is for each asset.

        # A dictionary of the vulnerability sets.
        # Not associated with exposures.
        # key - vulnerability set ID
        # value - vulnerability set instance
        self.vulnerability_sets = {}

        # A dictionary with keys being vulnerability_set_ids and
        # values being the exposure title that holds vulnerability
        # function ID's.
        self.vul_function_titles = {}

        # A dictionary of realised vulnerability curves, associated with the
        # exposure data.
        # key - intensity measure
        # value - realised vulnerability curve instance
        self.exposure_vuln_curves = None

    def save_exposure_atts(self, filename):
        """
        Save the exposure attributes, including latitude and longitude.
        The file type saved is based on the filename extension.
        Options
           '.npz': Save the arrays into a single file in uncompressed .npz
                   format.

        Args:
            filename: The file to be written.
        """

        write_dict = self.exposure_att.copy()
        write_dict[EX_LAT] = self.exposure_lat
        write_dict[EX_LONG] = self.exposure_long
        
        if filename[-4:] == '.csv':
            #  Only one dimension can be saved.  
            #  Average the results to the Site (first) dimension.
            for value in write_dict.intervalues:
                if len (value.shape) > 1:
                    #  TODO Log a message here
                    # Do a loop, taking the mean of the last axis
                    pass
        else:
            numpy.savez(filename, **write_dict)

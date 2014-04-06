# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Geoscience Australia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# W0221: 65:ConfigAwarePipeLine.run: Arguments number differs from
# overridden method
# pylint: disable=W0221
# I'm ok with .run having more arg's
# I should use the ABC though.

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

from core_hazimp.pipeline import PipeLineBuilder, PipeLine


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

        :param calcs: A list of Calculator instances

        :returns: A pipeline with the calcs in it, ready to process.
        """
        pipeline = ConfigAwarePipeLine(calcs)
        return pipeline


class ConfigAwareJob(object):

    """
    Build a job object that can inject more attributes into the job function
    call.
    """

    def __init__(self, job_instance, atts_to_add=None):
        """
        :param job_instance: An instance of a job.
        :param atts_to_add: A dictionary of attributes that will be passed
                            into the function all.
        """

        self.job_instance = job_instance
        self.atts_to_add = atts_to_add

    def __call__(self, *args, **job_kwargs):
        """
        Inject the atts_to_add to the job call.
        """
        if not self.atts_to_add is None:
            job_kwargs.update(self.atts_to_add)
        self.job_instance(*args, **job_kwargs)

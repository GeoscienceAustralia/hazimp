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
        if self.atts_to_add is not None:
            job_kwargs.update(self.atts_to_add)
        self.job_instance(*args, **job_kwargs)

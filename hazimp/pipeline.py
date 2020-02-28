# -*- coding: utf-8 -*-

# Copyright (c) 2010-2012, GEM Foundation.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=R0922
# Above disable doesn't seem to work.

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

import logging
log = logging.getLogger(__name__)

class PipeLine(object):

    """
    PipeLine allows to create a queue of
    jobs and execute them in order.
    """

    def __init__(self, jobs_list=None):
        """
        Initialize a PipeLine object having
        attributes: name and jobs, a list
        of callable objects.
        """

        self.jobs = []
        if jobs_list is not None:
            self.jobs = jobs_list

    def __eq__(self, other):
        """Equal operator for pipeline"""

        return self.jobs == other.jobs

    def __ne__(self, other):
        """Not equal operator for pipeline"""

        return not self.__eq__(other)

    def add_job(self, a_job):
        """Append a new job the to queue"""

        self.jobs.append(a_job)

    def run(self, context):
        """
        Run all the jobs in queue, where each job take input data and
        write the results of calculation in context.

        :param context: Context object holding the i/o data for the pipelines.
        """
        for job in self.jobs:
            log.info('Executing ' + type(getattr(job, 'job_instance', job)).__name__)
            job(context)

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
to process a series of :class:`Job` functions in a sequential
order. The order is determined by the queue of :class:`Job`.

Typically, a :class:`PipeLine` is created through pre-defined :ref:`templates`
that have been built into HazImp already. These templates ensure the correct
set of jobs are executed, in the correct order, for given use cases.

It's also possible to build a :class:`PipeLine` manually, using the
:meth:`PipeLine.add_job` method to add more jobs.

.. warning:: The order of jobs in a :class:`PipeLine` is important. The
   existing templates ensure correct order of the jobs. If creating a
   :class:`PipeLine` manually, the user will be responsible for ensuring
   the correct order of jobs. A `RuntimeError` is raised if the order is
   incorrect, and we recommend any new job pipelines are adapted from the
   existing templates.

.. note:: Currently we include the :class:`SaveProvenance` job in the
   templates, so a manually defined :class:`PipeLine` will have to explicitly
   include that at the end to ensure provenance information is captured.
"""

import logging
log = logging.getLogger(__name__)


class PipeLine(object):

    """
    PipeLine allows to create a queue of jobs and execute them in order.
    """

    def __init__(self, jobs_list=None):
        """
        Initialize a PipeLine object having
        attributes: name and jobs, a list
        of callable objects.

        :param job_list: A list of :class:`Job` objects, which are callable
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
            jobtype = type(getattr(job, 'job_instance', job)).__name__
            log.info(f'Executing {jobtype}')
            job(context)

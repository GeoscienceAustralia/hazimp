# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Geoscience Australia

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

"""
HazImp Templates Module

Templates convert a YAML template configuration file to jobs and calcs.
"""

from hazimp.config_build import add_job
from hazimp.templates.earthquake import _earthquake_v1_reader
from hazimp.templates.flood import (_flood_fabric_v2_reader,
                                    _flood_contents_v2_reader)
from hazimp.templates.wind import (_wind_v3_reader, _wind_v4_reader,
                                   _wind_v5_reader, _wind_nc_reader)
from hazimp.templates.constants import *


def _reader2(config: dict) -> list:
    """
    From an untemplated configuration list build the job list.

    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    for key, attributes in config.items():
        add_job(job_insts, key, atts=attributes)

    # For testing
    if False:
        for job in job_insts:
            print("*******************************************")
            print(("job.job_instance", job.job_instance))
            print(("job.atts_to_add", job.atts_to_add))
    return job_insts


READERS = {
    DEFAULT: _reader2,
    WINDV3: _wind_v3_reader,
    WINDV4: _wind_v4_reader,
    WINDV5: _wind_v5_reader,
    WINDNC: _wind_nc_reader,
    EARTHQUAKEV1: _earthquake_v1_reader,
    FLOODFABRICV2: _flood_fabric_v2_reader,
    FLOODCONTENTSV2: _flood_contents_v2_reader
}

# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Duncan Gray

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
Functions concerning the yaml configuration file.
"""

import yaml

from hazimp.templates import READERS, TEMPLATE, DEFAULT


def read_config_file(file_name: str) -> list:
    """
    Read the configuration file and return the info as a list.

    :param file_name: The yaml file.
    :returns: A list of the configuration file
    """
    with open(file_name, 'r') as config_file_handle:
        config = yaml.load(config_file_handle, Loader=yaml.FullLoader)

    return config


def instance_builder(config_list: list) -> list:
    """
    From the configuration list build and knowing
    the template, build the the job instances
    and add attributes in the config to the instances.

    :param config_list: A list describing the simulation.
    :returns: A list of job instances to process over.
    """
    assert isinstance(config_list, list)

    # Check that each element in the list is a single key dictionary.
    for jobcalc_dic in config_list:
        if not len(jobcalc_dic) == 1:
            msg = '\nConfig bad format. Forgotten dash? Two key dictionary?\n'
            msg += '%s \n' % jobcalc_dic
            raise RuntimeError(msg)

    try:
        template = config_list[0][TEMPLATE]
        del config_list[0]
    except KeyError:
        template = DEFAULT
    try:
        reader_function = READERS[str(template)]
    except KeyError:
        raise RuntimeError(
            'Invalid template name, %s in config file.' % template)

    config_dict = {k: v for item in config_list for k, v in list(item.items())}
    jobs = reader_function(config_dict)

    return jobs

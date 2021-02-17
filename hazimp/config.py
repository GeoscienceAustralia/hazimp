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


def read_file(file_name):
    """
    Read the configuration file and return the info as a dictionary.

    :param file_name: The yaml file.
    :returns: A dictionary of the configuration file
    """
    config_file_handle = open(file_name, 'r')
    config_inf = yaml.load(config_file_handle, Loader=yaml.FullLoader)
    if isinstance(config_inf, dict):
        config_dic = config_inf
    else:
        # Assume a list of dictionaries
        config_dic = {}
        for form in config_inf:
            config_dic.update(form)
    return config_dic


def read_config_file(file_name):
    """
    Read the configuration file and return the info as a list.

    :param file_name: The yaml file.
    :returns: A list of the configuration file
    """
    config_file_handle = open(file_name, 'r')
    the_conf = yaml.load(config_file_handle, Loader=yaml.FullLoader)
    # print "the_conf", the_conf
    return the_conf


def instance_builder(config_list):
    """
    From the configuration list build and knowing
    the template, build the the job instances
    and add attributes in the config to the instances.

    :param config_list: A list describing the simulation.
    :returns: A list of job instances to process over.
    """
    # print "config_list", config_list
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


def template_builder(config_dic):
    """
    From the configuration dictionary build and knowing
    the template, build the the job list
    and add predefined info to the config_dic.

    :param config_dic: A dictionary describing the simulation.
    :returns: A list of jobs to process over.
        ** The config_dic isn't returned, but it is modified.
    """
    try:
        template = config_dic[TEMPLATE]
        del config_dic[TEMPLATE]
    except KeyError:
        template = DEFAULT

    try:
        reader_function = READERS[str(template)]
    except KeyError:
        raise RuntimeError(
            'Invalid template name, %s in config file.' % template)

    jobs = reader_function(config_dic)
    return jobs

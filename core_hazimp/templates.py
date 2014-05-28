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
Functions converting a yaml template configuration file
to jobs and calcs.
"""

import os
from core_hazimp import misc
from core_hazimp.calcs.calcs import (STRUCT_LOSS, WATER_DEPTH, FLOOR_HEIGHT,
                                     FLOOR_HEIGHT_CALC)
from core_hazimp.config_build import find_atts, add_job
from core_hazimp.jobs.jobs import (LOADCSVEXPOSURE, LOADRASTER,
                                   LOADXMLVULNERABILITY, SIMPLELINKER,
                                   SELECTVULNFUNCTION,
                                   LOOKUP, SAVEALL, CONSTANT)

__author__ = 'u54709'

LOADWINDTCRM = 'load_wind_ascii'
LOADFLOODASCII = 'load_flood_ascii'
SAVE = 'save'


def _wind_v3_reader(config_list):
    """
    From a wind configuration list build the job list.

    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_atts(config_list, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_atts(config_list, LOADWINDTCRM)
    atts = {'file_list': file_list,
            'attribute_label': '0.2s gust at 10m height m/s'}
    add_job(job_insts, LOADRASTER, atts)

    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'synthetic_domestic_wind_vul_curves.xml')
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    atts = {'vul_functions_in_exposure': {
            'domestic_wind_2012':
            'WIND_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
            'domestic_wind_2012': 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)
    add_job(job_insts, STRUCT_LOSS)

    file_name = find_atts(config_list, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    return job_insts


def _flood_fabric_v2_reader(config_list):
    """
    This function does two things;
       * From a flood fabric template v1 configuration dictionary
       build the job list.
       * Set up the attributes of the jobs and calc's specifically
       for a flood study.
    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_atts(config_list, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_atts(config_list, LOADFLOODASCII)
    atts = {'file_list': file_list, 'attribute_label': WATER_DEPTH}
    add_job(job_insts, LOADRASTER, atts)
    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'fabric_flood_avg_curve.xml')
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    floor_height_value = find_atts(config_list, FLOOR_HEIGHT)
    atts = {'var': FLOOR_HEIGHT, 'value': floor_height_value}
    add_job(job_insts, CONSTANT, atts)

    add_job(job_insts, FLOOR_HEIGHT_CALC)

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    atts = {'vul_functions_in_exposure': {
            'structural_domestic_flood_2012':
            'FABRIC_FLOOD_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
            'structural_domestic_flood_2012': 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)
    add_job(job_insts, STRUCT_LOSS)

    file_name = find_atts(config_list, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    return job_insts


def _reader2(config_list):
    """
    From an untemplated configuration list build the job list.

    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    for jobcalc_dic in config_list:
        new_string = jobcalc_dic.keys()[0]
        atts = jobcalc_dic[new_string]
        add_job(job_insts, new_string, atts=atts)

    # For testing
    if False:
        for job in job_insts:
            print "*******************************************"
            print "job.job_instance", job.job_instance
            print "job.atts_to_add", job.atts_to_add
    return job_insts

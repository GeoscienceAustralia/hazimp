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

import logging
import os

from hazimp import misc
from hazimp.calcs.calcs import (WATER_DEPTH, FLOOR_HEIGHT,
                                FLOOR_HEIGHT_CALC)
from hazimp.config_build import add_job, find_attributes
from hazimp.jobs.jobs import (LOADCSVEXPOSURE, LOADRASTER,
                              LOADXMLVULNERABILITY, SIMPLELINKER,
                              SELECTVULNFUNCTION, RANDOM_CONSTANT,
                              LOOKUP, SAVEALL, CONSTANT, ADD,
                              MDMULT, PERMUTATE_EXPOSURE, AGGREGATE_LOSS,
                              CATEGORISE, SAVEPROVENANCE)

LOGGER = logging.getLogger(__name__)

__author__ = 'u12161'

TEMPLATE = 'template'
DEFAULT = 'default'
SAVE = 'save'
SAVEAGG = 'save_agg'
LOADWINDTCRM = 'load_wind'
HAZARDRASTER = 'hazard_raster'
CALCSTRUCTLOSS = 'calc_struct_loss'
CALCCONTLOSS = 'calc_cont_loss'
PERMUTATION = 'exposure_permutation'
VULNFILE = 'vulnerability_filename'
VULNSET = 'vulnerability_set'
WINDV3 = 'wind_v3'
WINDV4 = 'wind_v4'
WINDV5 = 'wind_v5'
WINDNC = 'wind_nc'

FLOODFABRICV2 = 'flood_fabric_v2'

REP_VAL_NAME = 'replacement_value_label'

FLOODCONTENTSV2 = 'flood_contents_v2'
INSURE_PROB = 'insurance_probability'
INSURED = 'insured'
UNINSURED = 'uninsured'

CONT_ACTIONS = 'contents_actions'
SAVE_CONT = 'save'
SAVEAGG_CONT = 'save_agg'
NO_ACTION_CONT = 'no_action'
EXPOSE_CONT = 'expose'
CONT_ACTION_COL = 'contents_action'
CONT_INSURANCE_COL = 'insurance_regime'
CONT_TEMP = 'regime_action'

AGGREGATION = 'aggregation'
AGGREGATE = 'aggregate'
TABULATE = 'tabulate'
CONT_MAP = {SAVE_CONT: "_SAVE", NO_ACTION_CONT: "_NOACTION",
            EXPOSE_CONT: "_EXPOSE"}
INSURE_MAP = {INSURED: "_INSURED", UNINSURED: "_UNINSURED"}


def _wind_v3_reader(config: dict) -> list:
    """
    DEPRECATED
    From a wind configuration list build the job list.

    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_attributes(config, [HAZARDRASTER, LOADWINDTCRM])
    atts = {'file_list': file_list,
            'attribute_label': '0.2s gust at 10m height m/s'}
    add_job(job_insts, LOADRASTER, atts)

    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'synthetic_domestic_wind_vul_curves.xml')
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = find_attributes(config, VULNSET)
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
        vulnerability_set_id: 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)

    atts_dict = find_attributes(config, CALCSTRUCTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'structural_loss_ratio', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})

    return job_insts


def _wind_v4_reader(config: dict) -> list:
    """
    From a wind configuration list build the job list.

    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_attributes(config, [HAZARDRASTER, LOADWINDTCRM])
    atts = {'file_list': file_list,
            'attribute_label': '0.2s gust at 10m height m/s'}
    add_job(job_insts, LOADRASTER, atts)

    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                find_attributes(config, VULNFILE))
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = find_attributes(config, VULNSET)
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
        vulnerability_set_id: 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)

    atts_dict = find_attributes(config, CALCSTRUCTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'structural_loss_ratio', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})

    return job_insts


def _wind_nc_reader(config: dict) -> list:
    """
    Build a job list from a wind configuration list for netcdf files.

    :param config_list: A list describing the simulation
    :returns: A list of jobs to process over
    """
    LOGGER.info("Using wind_nc template")
    job_insts = []
    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    atts = find_attributes(config, [HAZARDRASTER, LOADWINDTCRM])

    # Hard-coded at this time for wind
    atts['attribute_label'] = '0.2s gust at 10m height m/s'
    add_job(job_insts, LOADRASTER, atts)

    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                find_attributes(config, VULNFILE))
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = find_attributes(config, VULNSET)

    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}

    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
        vulnerability_set_id: 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    if PERMUTATION in config:
        atts = find_attributes(config, PERMUTATION)
        add_job(job_insts, PERMUTATE_EXPOSURE, atts)
    else:
        add_job(job_insts, LOOKUP)

    if CALCSTRUCTLOSS in config:
        atts_dict = find_attributes(config, CALCSTRUCTLOSS)
        if REP_VAL_NAME not in atts_dict:
            msg = f"Mandatory key not found in config file; {REP_VAL_NAME}"
            raise RuntimeError(msg)
        attributes = {'var1': 'structural_loss_ratio',
                      'var2': atts_dict[REP_VAL_NAME],
                      'var_out': 'structural_loss'}
        add_job(job_insts, MDMULT, attributes)

    if AGGREGATION in config:
        attributes = find_attributes(config, AGGREGATION)
        add_job(job_insts, AGGREGATE_LOSS, attributes)
        file_name = find_attributes(config, SAVEAGG)
        add_job(job_insts, SAVEAGG, {'file_name': file_name})

    if CATEGORISE in config:
        attributes = find_attributes(config, CATEGORISE)
        add_job(job_insts, CATEGORISE, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    if AGGREGATE in config:
        attributes = find_attributes(config, AGGREGATE)
        add_job(job_insts, AGGREGATE, attributes)

    if TABULATE in config:
        attributes = find_attributes(config, TABULATE)
        add_job(job_insts, TABULATE, attributes)

    # Eventually, this needs to be included in pipeline.Pipeline and
    # automatically added to the list of jobs
    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})

    return job_insts


def _wind_v5_reader(config: dict) -> list:
    """
    Build a job list from a wind configuration list.

    :param config_list: A list describing the simulation
    :returns: A list of jobs to process over
    """

    LOGGER.info("Using wind_v5 template")
    job_insts = []
    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_attributes(config, [HAZARDRASTER, LOADWINDTCRM])
    atts = {'file_list': file_list,
            'attribute_label': '0.2s gust at 10m height m/s'}
    add_job(job_insts, LOADRASTER, atts)

    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                find_attributes(config, VULNFILE))
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = find_attributes(config, VULNSET)
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
        vulnerability_set_id: 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    atts = find_attributes(config, PERMUTATION)
    add_job(job_insts, PERMUTATE_EXPOSURE, atts)

    atts_dict = find_attributes(config, CALCSTRUCTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'structural_loss_ratio', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    attributes = find_attributes(config, AGGREGATION)
    add_job(job_insts, AGGREGATE_LOSS, attributes)

    if CATEGORISE in config:
        attributes = find_attributes(config, CATEGORISE)
        add_job(job_insts, CATEGORISE, attributes)

    if TABULATE in config:
        attributes = find_attributes(config, TABULATE)
        add_job(job_insts, TABULATE, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVEAGG)
    add_job(job_insts, SAVEAGG, {'file_name': file_name})

    # Eventually, this needs to be included in pipeline.Pipeline and
    # automatically added to the list of jobs
    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})

    return job_insts


def _flood_fabric_v2_reader(config: dict) -> list:
    """
    This function does two things;
       * From a flood fabric template v2 configuration dictionary
       build the job list.
       * Set up the attributes of the jobs and calc's specifically
       for a flood study.
    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_attributes(config, HAZARDRASTER)
    atts = {'file_list': file_list, 'attribute_label': WATER_DEPTH}
    add_job(job_insts, LOADRASTER, atts)
    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'fabric_flood_avg_curve.xml')
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    floor_height_value = find_attributes(config, FLOOR_HEIGHT)
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

    atts_dict = find_attributes(config, CALCSTRUCTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'structural_loss_ratio', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})
    return job_insts

# this is disabling R:171, 0: Too many statements


def _flood_contents_v2_reader(config: dict) -> list:  # pylint: disable=R0915
    """
    This function does two things;
       * From a flood contents template v2 configuration dictionary
       build the job list.
       * Set up the attributes of the jobs and calc's specifically
       for a flood study.
    :param config_list: A list describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_insts = []

    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    file_list = find_attributes(config, HAZARDRASTER)
    atts = {'file_list': file_list, 'attribute_label': WATER_DEPTH}
    add_job(job_insts, LOADRASTER, atts)
    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'content_flood_avg_curve.xml')
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    floor_height_value = find_attributes(config, FLOOR_HEIGHT)
    atts = {'var': FLOOR_HEIGHT, 'value': floor_height_value}
    add_job(job_insts, CONSTANT, atts)

    add_job(job_insts, FLOOR_HEIGHT_CALC)

    # select save, nosave or expose
    atts = find_attributes(config, CONT_ACTIONS)
    probs = {}
    for key in CONT_MAP:
        if key not in atts:
            msg = '\nMandatory key not found in config file; %s\n' % key
            msg += 'Section; %s\n' % CONT_ACTIONS
            raise RuntimeError(msg)
        try:
            probs[CONT_MAP[key]] = atts[key]
        except TypeError:
            msg = "\nError: May be due to no spaces after ':' in YAML file\n"
            raise RuntimeError(msg)
    attributes = {'var': CONT_ACTION_COL, 'values': probs}
    add_job(job_insts, RANDOM_CONSTANT, attributes)

    # select insured or uninsured
    atts = find_attributes(config, INSURE_PROB)
    probs = {}
    for key in INSURE_MAP:
        if key not in atts:
            msg = '\nMandatory key not found in config file; %s\n' % key
            msg += 'Section; %s\n' % INSURE_PROB
            raise RuntimeError(msg)
        try:
            probs[INSURE_MAP[key]] = atts[key]
        except TypeError:
            msg = "\nError: May be due to no spaces after ':' in YAML file\n"
            raise RuntimeError(msg)

    attributes = {'var': CONT_INSURANCE_COL, 'values': probs}
    add_job(job_insts, RANDOM_CONSTANT, attributes)

    # combine columns to give constant_function_id
    attributes = {'var1': 'BUILDING_TYPE', 'var2': CONT_INSURANCE_COL,
                  'var_out': CONT_TEMP}
    add_job(job_insts, ADD, attributes)

    attributes = {'var1': CONT_TEMP, 'var2': CONT_ACTION_COL,
                  'var_out': 'CONTENTS_FLOOD_FUNCTION_ID'}

    add_job(job_insts, ADD, attributes)

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'CONTENTS_FLOOD_FUNCTION_ID'
    atts = {'vul_functions_in_exposure': {
        'contents_domestic_flood_2012':
            'CONTENTS_FLOOD_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    atts = {'variability_method': {
        'contents_domestic_flood_2012': 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)

    atts_dict = find_attributes(config, CALCCONTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'contents_loss_ratio', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'contents_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})
    return job_insts


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


READERS = {DEFAULT: _reader2,
           WINDV3: _wind_v3_reader,
           WINDV4: _wind_v4_reader,
           WINDV5: _wind_v5_reader,
           WINDNC: _wind_nc_reader,
           FLOODFABRICV2: _flood_fabric_v2_reader,
           FLOODCONTENTSV2: _flood_contents_v2_reader}

import logging
import os

from hazimp import misc
from hazimp.calcs.calcs import (WATER_DEPTH, FLOOR_HEIGHT,
                                FLOOR_HEIGHT_CALC)
from hazimp.config_build import find_attributes, add_job
from hazimp.jobs.jobs import (LOADCSVEXPOSURE, LOADRASTER,
                              LOADXMLVULNERABILITY,
                              CONSTANT, SIMPLELINKER,
                              SELECTVULNFUNCTION,
                              LOOKUP, MDMULT, RANDOM_CONSTANT, ADD,
                              TABULATE, PERMUTATE_EXPOSURE,
                              AGGREGATE_LOSS, CATEGORISE,
                              SAVEALL, SAVEPROVENANCE)
from hazimp.templates.constants import (HAZARDRASTER,
                                        CALCSTRUCTLOSS, CALCCONTLOSS,
                                        VULNSET, VULNFILE, VULNMETHOD,
                                        REP_VAL_NAME, PERMUTATION,
                                        AGGREGATION, AGGREGATE,
                                        SAVE, SAVEAGG
                                        )

LOGGER = logging.getLogger(__name__)

CONT_ACTIONS = 'contents_actions'
SAVE_CONT = 'save'
SAVEAGG_CONT = 'save_agg'
NO_ACTION_CONT = 'no_action'
EXPOSE_CONT = 'expose'
CONT_ACTION_COL = 'contents_action'
CONT_INSURANCE_COL = 'insurance_regime'
CONT_TEMP = 'regime_action'

INSURE_PROB = 'insurance_probability'
INSURED = 'insured'
UNINSURED = 'uninsured'

CONT_MAP = {
    SAVE_CONT: "_SAVE",
    NO_ACTION_CONT: "_NOACTION",
    EXPOSE_CONT: "_EXPOSE"
}

INSURE_MAP = {
    INSURED: "_INSURED",
    UNINSURED: "_UNINSURED"
}


def _flood_impact_reader(config: dict) -> list:
    """
    Build a job list from a flood impact configuration file. This template 
    assumes floor height is included in the exposure attributes, rather than
    assuming a fixed floor height for all buildings.

    :param config: a dict of jobs describing the pipeline
    :return: a list of job objects representing the pipeline

    """
    LOGGER.info("Using flood_impact template")
    job_insts = []
    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    atts = find_attributes(config, [HAZARDRASTER])

    atts['attribute_label'] = WATER_DEPTH
    add_job(job_insts, LOADRASTER, atts)

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'FLOOD_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]

    add_job(job_insts, FLOOR_HEIGHT_CALC)

    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'SURGE_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    if VULNMETHOD in vuln_atts:
        atts = {'variability_method': {
            vulnerability_set_id: vuln_atts[VULNMETHOD]}}
    else:
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
        attributes = {'var1': 'structural',
                      'var2': atts_dict[REP_VAL_NAME],
                      'var_out': 'structural_loss'}
        add_job(job_insts, MDMULT, attributes)

    if AGGREGATION in config:
        attributes = find_attributes(config, AGGREGATION)
        add_job(job_insts, AGGREGATE_LOSS, attributes)
        file_name = find_attributes(config, SAVEAGG)
        add_job(job_insts, SAVEAGG, {'file_name': file_name})

    categorise_attributes = {}
    if CATEGORISE in config:
        categorise_attributes = find_attributes(config, CATEGORISE)
        add_job(job_insts, CATEGORISE, categorise_attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    if AGGREGATE in config:
        attributes = find_attributes(config, AGGREGATE)
        attributes['categorise'] = categorise_attributes
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


def _flood_fabric_v2_reader(config: dict) -> list:
    """
    This function does two things::

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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})
    # The column title in the exposure file = 'FLOOD_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]

    # This adds an attribute to the context with 'var' name and constant
    # value 'value'
    floor_height_value = find_attributes(config, FLOOR_HEIGHT)
    atts = {'var': FLOOR_HEIGHT, 'value': floor_height_value}
    add_job(job_insts, CONSTANT, atts)

    add_job(job_insts, FLOOR_HEIGHT_CALC)

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'FABRIC_FLOOD_FUNCTION_ID'
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'FABRIC_FLOOD_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    if VULNMETHOD in vuln_atts:
        atts = {'variability_method': {
            vulnerability_set_id: vuln_atts[VULNMETHOD]}}
    else:
        atts = {'variability_method': {
            vulnerability_set_id: 'mean'}}
    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)

    atts_dict = find_attributes(config, CALCSTRUCTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'structural', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})
    return job_insts


def _flood_contents_v2_reader(config: dict) -> list:  # pylint: disable=R0915
    """
    This function does two things::

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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
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
    vulnerability_set_id = vuln_atts[VULNSET]
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'CONTENTS_FLOOD_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    if VULNMETHOD in vuln_atts:
        atts = {'variability_method': {
            vulnerability_set_id: vuln_atts[VULNMETHOD]}}
    else:
        atts = {'variability_method': {
            vulnerability_set_id: 'mean'}}

    add_job(job_insts, SELECTVULNFUNCTION, atts)

    add_job(job_insts, LOOKUP)

    atts_dict = find_attributes(config, CALCCONTLOSS)
    if REP_VAL_NAME not in atts_dict:
        msg = '\nMandatory key not found in config file; %s\n' % REP_VAL_NAME
        raise RuntimeError(msg)
    attributes = {
        'var1': 'contents', 'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'contents_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

    file_name = find_attributes(config, SAVE)
    base = os.path.splitext(file_name)[0]
    file_name = f"{base}.xml"
    add_job(job_insts, SAVEPROVENANCE, {'file_name': file_name})
    return job_insts

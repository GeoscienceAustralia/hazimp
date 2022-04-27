import logging
import os

from hazimp import misc
from hazimp.config_build import find_attributes, add_job
from hazimp.jobs.jobs import (LOADCSVEXPOSURE, LOADRASTER,
                              LOADXMLVULNERABILITY,
                              SIMPLELINKER, SELECTVULNFUNCTION,
                              LOOKUP, MDMULT, SAVEALL, SAVEPROVENANCE,
                              TABULATE, PERMUTATE_EXPOSURE,
                              AGGREGATE_LOSS, CATEGORISE)
from hazimp.templates.constants import (HAZARDRASTER, LOADWINDTCRM, VULNSET,
                                        CALCSTRUCTLOSS, REP_VAL_NAME, SAVE,
                                        VULNFILE, VULNMETHOD,
                                        PERMUTATION, AGGREGATION, SAVEAGG,
                                        AGGREGATE)

LOGGER = logging.getLogger(__name__)


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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
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
        'var1': 'structural',
        'var2': atts_dict[REP_VAL_NAME],
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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])

    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The vulnerabilitySetID from the nrml file = 'domestic_flood_2012'
    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
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
        'var1': 'structural',
        'var2': atts_dict[REP_VAL_NAME],
        'var_out': 'structural_loss'}
    add_job(job_insts, MDMULT, attributes)

    file_name = find_attributes(config, SAVE)
    add_job(job_insts, SAVEALL, {'file_name': file_name})

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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]
    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
    add_job(job_insts, SIMPLELINKER, atts)

    if VULNMETHOD in vuln_atts:
        atts = {'variability_method': {
            vulnerability_set_id: vuln_atts[VULNMETHOD]}}
    else:
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
        'var1': 'structural', 'var2': atts_dict[REP_VAL_NAME],
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

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'WIND_VULNERABILITY_FUNCTION_ID'
    vulnerability_set_id = vuln_atts[VULNSET]

    atts = {'vul_functions_in_exposure': {
        vulnerability_set_id:
            'WIND_VULNERABILITY_FUNCTION_ID'}}
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

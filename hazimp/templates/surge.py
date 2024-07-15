import logging
import os

from hazimp import misc
from hazimp.config_build import find_attributes, add_job
from hazimp.calcs.calcs import (WATER_DEPTH, FLOOR_HEIGHT,
                                FLOOR_HEIGHT_CALC)
from hazimp.jobs.jobs import (LOADCSVEXPOSURE, LOADRASTER,
                              LOADXMLVULNERABILITY,
                              SIMPLELINKER, SELECTVULNFUNCTION,
                              LOOKUP, MDMULT, SAVEALL, SAVEPROVENANCE,
                              TABULATE, PERMUTATE_EXPOSURE,
                              AGGREGATE_LOSS, CATEGORISE)
from hazimp.templates.constants import (HAZARDRASTER, VULNSET,
                                        CALCSTRUCTLOSS, REP_VAL_NAME, SAVE,
                                        VULNFILE, VULNMETHOD,
                                        PERMUTATION, AGGREGATION, SAVEAGG,
                                        AGGREGATE)

LOGGER = logging.getLogger(__name__)


def _surge_nc_reader(config: dict) -> list:
    """
    Build a job list from a surge configuration list for netcdf files.

    :param config_list: A list describing the simulation
    :returns: A list of jobs to process over
    """
    LOGGER.info("Using surge_nc template")
    job_insts = []
    atts = find_attributes(config, LOADCSVEXPOSURE)
    add_job(job_insts, LOADCSVEXPOSURE, atts)

    atts = find_attributes(config, [HAZARDRASTER])

    # Hard-coded at this time for wind
    atts['attribute_label'] = WATER_DEPTH
    add_job(job_insts, LOADRASTER, atts)

    vuln_atts = find_attributes(config, VULNFILE)
    vul_filename = os.path.join(misc.RESOURCE_DIR, vuln_atts['filename'])
    add_job(job_insts, LOADXMLVULNERABILITY, {'file_name': vul_filename})

    # The column title in the exposure file = 'SURGE_VULNERABILITY_FUNCTION_ID'
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

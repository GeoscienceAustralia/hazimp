# -*- coding: utf-8 -*-


"""
Functions concerning the yaml configuration file.

"""

import os
import yaml
import copy

from core_hazimp.calcs.calcs import CALCS
from core_hazimp.jobs.jobs import (JOBS, LOADRASTER, LOADCSVEXPOSURE,
    LOADXMLVULNERABILITY, SIMPLELINKER, SELECTVULNFUNCTION,
    LOOKUP, SAVEALL, JOBSKEY)
from core_hazimp.calcs.calcs import STRUCT_LOSS
from core_hazimp import misc
from core_hazimp import spell_check

DEFAULT = 'default'
LOADWINDTCRM = 'load_wind_tcrm_ascii'
TEMPLATE = 'template'
WINDV1 = 'windv1'
SAVE = 'save'

# The complete list of first level key names in the post template config dic
CONFIGKEYS = list(JOBS.keys()) + list(CALCS.keys()) + [JOBSKEY]
SPELLCHECK = spell_check.SpellCheck(CONFIGKEYS)


def read_file(file_name):
    """
    Read the configuration file and return the info as a dictionary.

    :param file_name: The yaml file.
    :returns: A dictionary of the configuration file
    """
    config_file_handle = open(file_name, 'r')
    config_dic = yaml.load(config_file_handle)

    return config_dic


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


def _reader1(config_dic):
    """
    From a version 1 configuration dictionary build the job list.

    :param config_dic: A dictionary describing the simulation.
    :returns: A list of jobs to process over.
    """

    try:
        job_names = config_dic[JOBSKEY]
    except KeyError:
        raise RuntimeError(
            'No jobs label in config file.')

    return get_job_or_calcs(job_names)


def _wind_v1_reader(config_dic):
    """
    From a wind v1 configuration dictionary build the job list.

    :param config_dic: A dictionary describing the simulation.
    :returns: A list of jobs to process over.
    """
    job_names = [LOADCSVEXPOSURE, LOADRASTER, LOADXMLVULNERABILITY,
                 SIMPLELINKER, SELECTVULNFUNCTION, LOOKUP, STRUCT_LOSS,
                 SAVEALL]
    vul_filename = os.path.join(misc.RESOURCE_DIR,
                                'domestic_wind_vul_curves.xml')

    try:
        file_list = config_dic[LOADWINDTCRM]
    except KeyError:
        msg = '\nMandatory key not found in config file; %s \n' % LOADWINDTCRM
        raise RuntimeError(msg)

    config_dic[LOADRASTER] = {
        'file_list': file_list,
        'attribute_label': '0.2s gust at 10m height m/s'}
    del config_dic[LOADWINDTCRM]
    config_dic[LOADXMLVULNERABILITY] = {
        'file_name': vul_filename}
    config_dic[SIMPLELINKER] = {'vul_functions_in_exposure': {
                                'domestic_wind_2012':
                                'WIND_VULNERABILITY_FUNCTION_ID'}}
    config_dic[SELECTVULNFUNCTION] = {'variability_method': {
                                      'domestic_wind_2012': 'mean'}}

    try:
        file_name = config_dic[SAVE]
    except KeyError:
        msg = '\nMandatory key not found in config file; %s \n' % SAVE
        raise RuntimeError(msg)

    config_dic[SAVEALL] = {'file_name': file_name}
    del config_dic[SAVE]
    return get_job_or_calcs(job_names)


def get_job_or_calcs(job_names):
    """
    Given a list of job or calc names, return a list of job or calc
    instances.

    :param name: The name if a job or calc.
    :returns: A list of Job or Calc instances.
    """
    jobs = []
    for job_name in job_names:
        jobs.append(get_job_or_calc(job_name))

    return jobs


def get_job_or_calc(name):
    """
    Given a job or calc name, return the job or calc instance.

    :param name: The name if a job or calc.
    :returns: A list of Job or Calc instance.
    """
    try:
        job = CALCS[name]
    except KeyError:
        try:
            job = JOBS[name]
        except KeyError:
            raise RuntimeError(
                'Invalid job name, %s in config file.' % name)
    return job


def validate_config(config_dic):
    """
    Check the config_dic for various errors.

    :param config_dic: A dictionary describing the simulation.
    """
    check_files_to_load(config_dic)
    check_1st_level_keys(config_dic)
    check_attributes(config_dic)


def file_can_open(file2load):
    """
    Check if a file can be opened.
    :param file2load: file.
    :returns: True if file2load can be opened.
    """
    try:
        with open(file2load) as _:
            pass
    except IOError:
        return False
    return True


def check_files_to_load(config_dic):
    """
    Check the context, based on the config file.

    This function relies on some assumptions.
    All jobs/calcs that load files label the files as;
       file_name OR
       file_list - for a list of files

    :param config_dic: A dictionary describing the simulation.
    :raises: RuntimeError
    """
    bad_files = []
    for key, value in config_dic.iteritems():
        if isinstance(value, dict) and 'save' not in key:
            if 'file_name' in value:
                file2load = value['file_name']
                if not file_can_open(file2load):
                    bad_files.append(file2load)
            elif 'file_list' in value:
                files2load = value['file_list']
                for file2load in files2load:
                    if not file_can_open(file2load):
                        bad_files.append(file2load)
    if len(bad_files) == 1:
        raise RuntimeError(
            'Invalid file name, %s in config file.' % bad_files[0])
    elif len(bad_files) > 1:
        raise RuntimeError(
            'Invalid files in config file;\n %s ' % bad_files)
    return True  # for testing


def check_1st_level_keys(config_dic):
    """
    Check the context, based on the config file.

    This function relies on some assumptions.
    All jobs/calcs that load files label the files as;
       file_name OR
       file_list - for a list of files

    :param config_dic: A dictionary describing the simulation.
    :raises: RuntimeError
    """

    for key in config_dic:
        if not key in SPELLCHECK.base_words:
            meantkey = SPELLCHECK.correct(key)
            msg = '\nInvalid key in config file; %s \n' % key
            if meantkey == key:
                # There was no suggested word
                raise RuntimeError(msg)
            else:
                msg += 'Did you mean; %s?' % meantkey
                raise RuntimeError(msg)


def check_attributes(config_dic):
    """
    Check the attributes of the jobs/cal functions for spelling.
    It will check if all attributes are
    * Missing when they are mandatory
    * typo args

    :param config_dic: A dictionary describing the simulation.
    :raises: RuntimeError
    """

    # Need to catch;
    # Missing mandatory args
    # typo args
    for key in config_dic:
        if key == JOBSKEY:
            pass
        else:
            job_calc_instance = get_job_or_calc(key)
            args, defaults = job_calc_instance.get_required_args_no_context()
            unchecked_config_args = copy.copy(config_dic[key])

            # Make sure the mandatory args are there
            # And remove them from the unchecked list
            for arg_call in args:
                try:
                    del unchecked_config_args[arg_call]
                except KeyError:
                    # An argument that must be present was not present.
                    msg = 'The job %s is missing the parameter %s' % (key,
                                                                      arg_call)
                    raise RuntimeError(msg)

            # remove default parameters from the unchecked list
            for default_call in defaults:
                try:
                    del unchecked_config_args[default_call]
                except KeyError:
                    pass

            # If the are still unchecked args then there is an error
            if len(unchecked_config_args) > 0:
                msg = 'The job %s has the following unkown parameters;\n' % key
                for unknown_arg in unchecked_config_args:
                    msg += '%s\n' % unknown_arg
                raise RuntimeError(msg)


READERS = {DEFAULT: _reader1,
           WINDV1: _wind_v1_reader}

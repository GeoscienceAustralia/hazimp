# -*- coding: utf-8 -*-

# Copyright (c) 2010-2012, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.


"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""
import hazimp

import yaml

class PluginBuilder(PipeLineBuilder):
    """
    Builds a plugin pipeline
    """


class PreprocessingBuilder(PipeLineBuilder):
    """
    PreprocessingBuilder allows to build a
    preprocessing pipeLine
    """

    PREPROCESSING_JOBS_KEY = 'preprocessing_jobs'
    PPROCESSING_RESULT_KEY = 'pprocessing_result_file'

    def build(self, config):

        # Checks if source model is defined
        if config['source_model_file']:
            source_model_creation = read_source_model
        else:
            source_model_creation = create_default_source_model

        # Add compulsory jobs to the pipeline'])
        pipeline = PipeLine([read_eq_catalog, source_model_creation,
                    create_catalog_matrix, create_default_values])

        # Add preprocessing jobs
        if config[PreprocessingBuilder.PREPROCESSING_JOBS_KEY]:
            self.append_jobs(pipeline,
                    config[PreprocessingBuilder.PREPROCESSING_JOBS_KEY])

            # Add store eq catalog jobs if result file is defined
            if config[PreprocessingBuilder.PPROCESSING_RESULT_KEY]:
                pipeline.add_job(self.map_job_callable['Create_eq_vector'])
                pipeline.add_job(self.map_job_callable['Store_eq_catalog'])
                pipeline.add_job(
                    self.map_job_callable['Store_completeness_table'])
        else:
            if config['completeness_table_file']:
                pipeline.add_job(
                    self.map_job_callable['Retrieve_completeness_table'])

        return pipeline


class ProcessingBuilder(PipeLineBuilder):
    """
    ProcessingBuilder allows to build a
    processing pipeLine
    """

    PROCESSING_JOBS_CONFIG_KEY = 'processing_jobs'

    def build(self, config):
        pipeline = PipeLine()

        if config[ProcessingBuilder.PROCESSING_JOBS_CONFIG_KEY]:
            self.append_jobs(pipeline,
                    config[ProcessingBuilder.PROCESSING_JOBS_CONFIG_KEY])

        return pipeline


class Context(object):
    """
    Context allows to read the config file
    and store preprocessing/processing steps
    intermediate results.
    """

    def __init__(self, config_filename=None):
        self.config = dict()
        self.map_sc = {'gardner_knopoff': gardner_knopoff_decluster,
                        'afteran': afteran_decluster,
                        'stepp': stepp_analysis,
                        'recurrence': recurrence_analysis,
                        'select_eq_vector': selected_eq_flag_vector,
                        'maximum_magnitude': maximum_magnitude_analysis}

        if config_filename:
            config_file = open(config_filename, 'r')
            self.config = yaml.load(config_file)

        self.eq_catalog = None
        self.sm_definitions = None
        self.catalog_matrix = None
        self.working_catalog = None
        self.completeness_table = None


class Workflow(object):
    """
    Workflow is the object responsible
    for dealing with preprocessing and
    processing pipelines
    """

    def __init__(self, preprocessing_pipeline, processing_pipeline):
        self.preprocessing_pipeline = preprocessing_pipeline
        self.processing_pipeline = processing_pipeline

    def start(self, context, catalog_filter):
        """
        Execute the main workflow
        """
        self.preprocessing_pipeline.run(context)
        if context.config['apply_processing_jobs']:
            for sm, filtered_eq in catalog_filter.filter_eqs(
                    context.sm_definitions, context.working_catalog):

                context.cur_sm = sm
                context.current_filtered_eq = filtered_eq
                self.processing_pipeline.run(context)

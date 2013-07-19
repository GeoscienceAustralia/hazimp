# -*- coding: utf-8 -*-
"""
The main entry point for the hazard impact tool.
"""

from core_hazimp import console
from core_hazimp import workflow
from core_hazimp import config


def main(config_dic=None, config_file=None):
    """
    Run the HazImp tool, based on the config info.

    :param config_dic: The configuration info, as a dictionary.
    :param config_file: The configuration info, as a file location.
    :returns: The config dictionary.
    """
    if config_file:
        config_dic = config.read_file(config_file)

    if config_dic is None:
        raise RuntimeError('No configuration information.')
    context = workflow.Context()
    calc_jobs = config.template_builder(config_dic)  # config_dic modified
    config.validate_config(config_dic)
    pipe_factory = workflow.ConfigPipeLineBuilder()
    pipeline = pipe_factory.build(calc_jobs)
    pipeline.run(context, config_dic)
    return context

############################################################################
if __name__ == "__main__":
    CMD_LINE_ARGS = console.cmd_line()
    if CMD_LINE_ARGS:
        main(config_file=CMD_LINE_ARGS.config_file[0])

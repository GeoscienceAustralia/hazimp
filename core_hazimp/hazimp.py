# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Geoscience Australia

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

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
from core_hazimp import context
from core_hazimp import config
from core_hazimp import pipeline


def start(config_list=None, config_file=None, cont_in=None):
    """
    Run the HazImp tool, based on the config info.

    :param config_list: The configuration info, as a list.
    :param config_file: The configuration info, as a file location.
    :param cont_in: Only used in testing. A context instance.
    :returns: The config dictionary.
    """
    if config_file:
        config_list = config.read_config_file(config_file)

    if config_list is None:
        raise RuntimeError('No configuration information.')

    if cont_in is None:
        cont_in = context.Context()
    calc_jobs = config.instance_builder(config_list)
    the_pipeline = pipeline.PipeLine(calc_jobs)
    the_pipeline.run(cont_in)
    return cont_in

############################################################################
if __name__ == "__main__":
    CMD_LINE_ARGS = console.cmd_line()
    if CMD_LINE_ARGS:
        # main(config_file=CMD_LINE_ARGS.config_file[0])
        start(config_file=CMD_LINE_ARGS.config_file[0])

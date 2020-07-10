# -*- coding: utf-8 -*-

# Copyright (C) 2020  Geoscience Australia

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
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)
from hazimp import console, misc
from hazimp import context
from hazimp import config
from hazimp import pipeline

import numpy
import logging
from functools import wraps, reduce
import time
import sys



def timer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        t1 = time.time()
        res = f(*args, **kwargs)

        tottime = time.time() - t1
        msg = "%02d:%02d:%02d " % \
          reduce(lambda ll, b : divmod(ll[0], b) + ll[1:],
                        [(tottime,), 60, 60])

        logging.info("Time for {0}: {1}".format(f.__name__, msg) )
        return res

    return wrap

# This;
#  numpy.column_stack((body, only_1d))
# loses significant figures in numpy1.6
# numpy1.7 and 1.8 not checked
NUMVER = numpy.__version__
NUMVER = NUMVER.split('.')
if NUMVER[0] == '1' and int(NUMVER[1]) < 9:
    raise RuntimeError("Must use numpy 1.9 or greater")

@timer
def start(config_list=None, config_file=None, cont_in=None):
    """
    Run the HazImp tool, based on the config info.

    :param config_list: The configuration info, as a list.
    :param config_file: The configuration info, as a file location.
    :param cont_in: Only used in testing. A context instance.
    :returns: The config dictionary.
    """
    if config_file:
        config_file = misc.download_file_from_s3_if_needed(config_file)
        config_list = config.read_config_file(config_file)

    if isinstance(config_list, dict):
        msg = "Bad configuration file. \n"
        msg += "Add a dash ( - ) before each variable. e.g. - template: flood"
        raise RuntimeError(msg)

    if config_list is None:
        raise RuntimeError('No configuration information.')

    if cont_in is None:
        cont_in = context.Context()
    # TODO: Make the entity name a tailored variable
    cont_in.set_prov_label("HazImp_analysis")
    calc_jobs = config.instance_builder(config_list)
    the_pipeline = pipeline.PipeLine(calc_jobs)
    the_pipeline.run(cont_in)

    return cont_in

def cli():
    "Command-line interface to hazimp package"
    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    CMD_LINE_ARGS = console.cmd_line()
    if CMD_LINE_ARGS:
        start(config_file=CMD_LINE_ARGS.config_file[0])

if __name__ == "__main__":
    cli()

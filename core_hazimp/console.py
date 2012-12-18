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
A set of utility functions for cmdline
"""

import os
import sys
import argparse


def build_cmd_parser():
    """
    Create a simple parser for cmdline
    """

    parser = argparse.ArgumentParser(prog='Hazimp')
    parser.add_argument('-c', '--config-file',
                        dest='config_file',
                        nargs=1,
                        help="""Specify the configuration
                        file (i.e. config.yml)""")

    # parser.add_argument('-d', '--detailed', help="""Show detailed
    #                     information about the workflow """,
    #                     action='store_true')

    parser.add_argument('-v', '--version',
                        action='version',
                        version="%(prog)s 0.1")
    return parser


def cmd_line():
    """
    Return cmdline input argument
    after checking the proper input
    has been given.
    """

    parser = build_cmd_parser()
    args = None
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if not os.path.exists(args.config_file[0]):
            print 'Error: non existent config file\n'
            parser.print_help()

    return args



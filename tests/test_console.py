# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Geoscience Australia

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
Test HazImp Console
"""

import os
import tempfile
import unittest
from pprint import pprint
from unittest.mock import patch

from hazimp.console import cmd_line
from hazimp.validator import Validator, NRML_SCHEMA
from tests import CWD


class TestValidator(unittest.TestCase):
    def setUp(self):
        pass

    @patch('sys.argv', ['hazimp'])
    def test_command_line_help(self):
        args = cmd_line()
        self.assertIsNone(args)

    @patch('sys.argv', ['hazimp', '-v'])
    def test_command_line_version(self):
        with self.assertRaises(SystemExit) as context:
            cmd_line()

        self.assertEqual(context.exception.code, 0)

    @patch('sys.argv', ['hazimp', '-c', str(CWD / 'data/template.yaml')])
    def test_command_line_args(self):
        args = cmd_line()

        self.assertEqual(str(CWD / 'data/template.yaml'), args.config_file[0])


if __name__ == '__main__':
    unittest.main()

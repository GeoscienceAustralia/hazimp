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

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test hazimp.
"""

  # can now use print()

import unittest
import tempfile
import os

import scipy

from hazimp import context
from hazimp import main

from hazimp import templates


class TestHazimp(unittest.TestCase):

    """
    Test Hazimp.
    """

    def test_start(self):
        config_list = [{templates.TEMPLATE: templates.DEFAULT},
                       {'constant': {'var': 'c_test', 'value': 7}},
                       {'add_test': None},
                       {'multiply_test': None}]
        a_test = 5
        b_test = 2
        cont_in = context.Context()
        cont_in.exposure_att = {'a_test': a_test, 'b_test': b_test}
        cont_in.exposure_long = scipy.asarray([11.0])

        cont_in = main.start(config_list=config_list, cont_in=cont_in)
        self.assertEqual(cont_in.exposure_att['d_test'], 35)
        self.assertEqual(cont_in.exposure_att['c_test'], 7)

    def test_startII(self):

        # The config file
        f = tempfile.NamedTemporaryFile(
            suffix='.yaml',
            prefix='HAZIMPt_test_hazimp',
            delete=False,
            mode='w+t')

        print(' - ' + templates.TEMPLATE + ': ' + templates.DEFAULT, file=f)
        print(' - constant : ', file=f)
        print('    var : c_test', file=f)
        print('    value : 7  ', file=f)
        print(' -  add_test:', file=f)
        print(' -  multiply_test:', file=f)
        f.close()

        a_test = 5
        b_test = 2
        cont_in = context.Context()
        cont_in.exposure_long = scipy.asarray([11.0])

        cont_in.exposure_att = {'a_test': a_test, 'b_test': b_test}

        cont_in = main.start(config_file=f.name, cont_in=cont_in)
        os.remove(f.name)
        self.assertEqual(cont_in.exposure_att['d_test'], 35)  # 7 * 5
        self.assertEqual(cont_in.exposure_att['c_test'], 7)  # 5 + 2
# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestHazimp, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

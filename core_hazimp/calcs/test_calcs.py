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

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases

"""
Test the calcs module.
"""

import unittest
import numpy

from core_hazimp.calcs.calcs import CALCS
from core_hazimp.calcs import calcs


class Dummy(object):

    """
    Dummy class for testing
    """

    def __init__(self):
        pass


class TestCalcs(unittest.TestCase):

    """
    Test the calcs module
    """

    def test_Add(self):
        inst = CALCS['add_test']
        context = Dummy
        context.exposure_att = {'a_test': 5, 'b_test': 20}
        inst(context)
        self.assertEqual(context.exposure_att['c_test'], 25)
        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['c_test'])

    def test_AddII(self):
        inst = CALCS['add_test']
        context = Dummy
        context.exposure_att = {'a_test': numpy.array([1, 2]),
                                'b_test': numpy.array([3, 4])}
        inst(context)
        self.assertTrue(numpy.allclose(context.exposure_att['c_test'],
                                       numpy.array([4, 6])))
        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['c_test'])

    def test_AddIII(self):
        # FIXME convert to strings
        inst = CALCS['add_test']
        context = Dummy
        context.exposure_att = {'a_test': numpy.array(['a', 'b']),
                                'b_test': numpy.array(['c', 'd'])}
        inst(context)
        self.assertEqual(context.exposure_att['c_test'].tolist(),
                         ['ac', 'bd'])
        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['c_test'])

    def test_MultipleValuesTest(self):
        # Not such a good test though
        inst = CALCS['multiple_values_test']
        context = Dummy
        context.exposure_att = {'a_test': 5, 'b_test': 20}
        inst(context)
        self.assertEqual(context.exposure_att['e_test'], 5)
        self.assertEqual(context.exposure_att['f_test'], 20)

        self.assertEqual(inst.context_args_in, ['a_test', 'b_test'])
        self.assertEqual(inst.args_out, ['e_test', 'f_test'])

    def test_ConstantTestTest(self):
        inst = CALCS['constant_test']
        context = Dummy
        context.exposure_att = {'a_test': 5, 'b_test': 20}
        inst(context, **{'constant': 5})
        self.assertEqual(context.exposure_att['g_test'], 5 * 2)

    def test_CalcLoss(self):
        inst = CALCS[calcs.STRUCT_LOSS]
        context = Dummy
        context.exposure_att = {'structural_loss_ratio': 5,
                                'REPLACEMENT_VALUE': 20}
        inst(context)
        self.assertEqual(context.exposure_att['structural_loss'], 5 * 20)

#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestCalcs, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

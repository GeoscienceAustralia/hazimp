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

# pylint: disable=W0221
# Since the arguemts for __call__ will change from class to calss

"""
Calculations


"""

import sys

from core_hazimp.jobs.jobs import Job
from core_hazimp import misc

STRUCT_LOSS = 'structural_loss'


class Calculator(Job):

    """
    Abstract Calculator class. Should use abc then.
    """

    def __init__(self):
        """
        Initalise a Calculator object.
        """
        super(Calculator, self).__init__()

    def calc(self):
        """
        The actual calculation.
        """
        pass

    def __call__(self, context, **kwargs):
        """
        This calls calc, passing in context.exposure_att and **kwargs.
        """
        args_in = []
        for job_arg in self.context_args_in:
            # A calc with no input is ok.
            if job_arg not in context.exposure_att:
                raise RuntimeError(
                    'No correct variables, %s .' % job_arg)
            args_in.append(context.exposure_att[job_arg])
        args_out = self.calc(*args_in, **kwargs)
        assert len(args_out) == len(self.args_out)
        for i, arg_out in enumerate(self.args_out):
            context.exposure_att[arg_out] = args_out[i]


class Add(Calculator):

    """
    Simple test class, adding args together.
    """

    def __init__(self):
        super(Add, self).__init__()
        self.args_out = ['c_test']
        self.context_args_in = ['a_test', 'b_test']
        self.call_funct = 'add_test'

    def calc(self, a_test, b_test):
        """
        Add args
        """
        # This needs to return a list, since it is a list of outputs
        return [misc.add(a_test, b_test)]


class MultiplyTest(Calculator):

    """
    Simple test class, multiplying args.
    """

    def __init__(self):
        super(MultiplyTest, self).__init__()
        self.context_args_in = ['a_test', 'c_test']
        self.args_out = ['d_test']
        self.call_funct = 'multiply_test'

    def calc(self, a_test, c_test):
        """
        Multiply args
        """
        return [a_test * c_test]


class MultipleValuesTest(Calculator):

    """
    Simple test class, returning two values.
    """

    def __init__(self):
        super(MultipleValuesTest, self).__init__()
        self.context_args_in = ['a_test', 'b_test']
        self.args_out = ['e_test', 'f_test']
        self.call_funct = 'multiple_values_test'

    def calc(self, a_test, b_test):
        """
        Return two values
        """
        return [a_test, b_test]


class ConstantTest(Calculator):

    """
    Simple test class, returning two values.
    """

    def __init__(self):
        super(ConstantTest, self).__init__()
        self.context_args_in = []
        self.args_out = ['g_test']
        self.call_funct = 'constant_test'

    def calc(self, constant=None):
        """
        Return two values
        """
        return [constant * 2]


class CalcLoss(Calculator):

    """
    Multiply the structural_loss_ratio and the structural_value to calc
    the structural_loss.
    """

    def __init__(self):
        super(CalcLoss, self).__init__()
        self.context_args_in = ['structural_loss_ratio', 'REPLACEMENT_VALUE']
        self.args_out = ['structural_loss']
        self.call_funct = STRUCT_LOSS

    def calc(self, structural_loss_ratio, structural_value):
        """
        Return two values
        """

        return [structural_loss_ratio * structural_value]


CALCS = misc.instanciate_classes(sys.modules[__name__])

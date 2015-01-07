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
FLOOR_HEIGHT_CALC = 'floor_height'
WATER_DEPTH = 'water_depth'
FLOOR_HEIGHT = 'floor_height_(m)'
FLOOD_X_AXIS = 'water depth above ground floor (m)'
# 'ground_floor_water_depth_m'


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

        Note, the returned value is a LIST.
        This is done so multiple values can be returned.
        """
        pass

    def __call__(self, context, **kwargs):
        """
        This calls calc, passing in context.exposure_att and **kwargs.
        """
        args_in = []
        for job_arg in self.context_args_in:
            # A calc with no input is ok.
            #print (job_arg)
            if job_arg not in context.exposure_att:
                raise RuntimeError(
                    'No correct variables, %s .' % job_arg)
            args_in.append(context.exposure_att[job_arg])
        args_out = self.calc(*args_in, **kwargs)
        assert len(args_out) == len(self.args_out)
        for i, arg_out in enumerate(self.args_out):
            context.exposure_att[arg_out] = args_out[i]


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
        Multiply values element-wise
        :param a_test:
        :param c_test:
        :return: the product of a_test and c_test
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
        Testing how two values could be returned.

        :param a_test:
        :param b_test:
        :return:
        """
        return [a_test, b_test]


class ConstantTest(Calculator):

    """
    Simple test class, returning two values.
    A Constant class to use is in the jobs file
    """

    def __init__(self):
        super(ConstantTest, self).__init__()
        self.context_args_in = []
        self.args_out = ['g_test']
        self.call_funct = 'constant_test'

    def calc(self, constant=None):
        """
        Testing returning a constant value, multiplied by two.
        :param constant:
        :return:
        """
        return [constant * 2]


class Add(Calculator):

    """
    Simple test class, adding args together.

    Note, jobs has a general adding method.
    """

    def __init__(self):
        super(Add, self).__init__()
        self.args_out = ['c_test']
        self.context_args_in = ['a_test', 'b_test']
        self.call_funct = 'add_test'

    def calc(self, a_val, b_val):
        # This needs to return a list, since it is a list of outputs
        """
        Add a_test and b_test.

        :param a_val: Can be a number or a string.
        :param b_val: Can be a number or a string.
        :return: Return the sum of a_test and b_test.
        """
        return [misc.add(a_val, b_val)]


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
        Calculate the structural loss, given the structural value and
            the loss ratio.
        :param structural_loss_ratio:
        :param structural_value:
        :return: The structural loss
        """
        return [structural_loss_ratio * structural_value]

class CalcContentsLoss(Calculator):

    """
    Multiply the structural_loss_ratio and the structural_value to calc
    the structural_loss.
    """

    def __init__(self):
        super(CalcLoss, self).__init__()
        self.context_args_in = ['contents_loss_ratio', 'CONTENTS_VALUE']
        self.args_out = ['contents_loss']
        self.call_funct = STRUCT_LOSS

    def calc(self, structural_loss_ratio, structural_value):
        """
        Calculate the structural loss, given the structural value and
            the loss ratio.
        :param structural_loss_ratio:
        :param structural_value:
        :return: The structural loss
        """
        return [structural_loss_ratio * structural_value]


class CalcFloorInundation(Calculator):

    """
    Calculate the water depth above ground floor;
    water depth(m) - floor height(m) = water depth above ground floor(m)
    """

    def __init__(self):
        super(CalcFloorInundation, self).__init__()
        self.context_args_in = [WATER_DEPTH, FLOOR_HEIGHT]
        self.args_out = [FLOOD_X_AXIS]
        self.call_funct = FLOOR_HEIGHT_CALC

    def calc(self, water_depth, floor_height):
        """
        Note the water depth and floor height have to have the same datum.
        e.g. above ground or Australian Height Datum

        :param water_depth: water depth (m)
        :param floor_height: floor height (m)
        :return: water depth above ground floor (m)
        """
        return [water_depth - floor_height]

CALCS = misc.instanciate_classes(sys.modules[__name__])

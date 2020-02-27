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
# pylint: disable=R0801
#:  Can not seem to locally disable this warning.

"""
Test the calcs module.
"""

import unittest
import numpy

from hazimp.jobs import plane_from_points


class TestPfP(unittest.TestCase):

    """
    Test the calcs module
    """

    def test_origin_plan(self):
        xyz = numpy.array([
            [0, 0, 0],
            [0, 1, 1],
            [0, 2, 2],
            [1, 0, 0],
            [1, 1, 1],
            [1, 2, 2],
            [2, 0, 0],
            [2, 1, 1],
            [2, 2, 2]
        ])
        results = plane_from_points.fit_plane_svd(xyz)
        # v = results
        # v[0](x) + v[1](y) - v[2](z) = 0
        # v[0] = 0
        # v[1]/v[2] = -1 But what are the values?
        self.assertTrue(numpy.allclose(results[0],
                                       numpy.asarray([0.0])))
        self.assertTrue(numpy.allclose(results[1] / results[2],
                                       numpy.asarray([-1.0])))

    def test_origin_planII(self):
        xyz = numpy.array([
            [0, 0, 0],
            [0, 1, -10],
            [0, 2, -20],
            [1, 0, -100],
            [1, 1, -110],
            [1, 2, -120],
            [2, 0, -200],
            [2, 1, -210],
            [2, 2, -220]
        ])

        results = plane_from_points.fit_plane_svd(xyz)
        # v = results
        # (v[0](x) + v[1](y))/ - v[2] = z
        # v[0]/v[2] = 100
        # v[1]/v[2] = 10
        self.assertTrue(numpy.allclose(results[0] / results[2],
                                       numpy.asarray([100.0])))
        self.assertTrue(numpy.allclose(results[1] / results[2],
                                       numpy.asarray([10.0])))

    def test_plan(self):
        xyz = numpy.array([
            [0, 0, -1000],
            [0, 1, -1010],
            [0, 2, -1020],
            [1, 0, -1100],
            [1, 1, -1110],
            [1, 2, -1120],
            [2, 0, -1200],
            [2, 1, -1210],
            [2, 2, -1220]
        ])
        # z = -1000 + (-100)x + (-10)y
        plane = plane_from_points.Plane(xyz)
        x = numpy.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        y = numpy.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        x = xyz[:, 0]
        y = xyz[:, 1]
        actual_z = xyz[:, 2]
        est_z = plane.estimate_z(x, y)
        self.assertTrue(numpy.allclose(est_z, actual_z))
        x = numpy.array([3, 4])
        y = numpy.array([4, 5])
        actual_z = numpy.array([-1340, -1450])
        est_z = plane.estimate_z(x, y)
        self.assertTrue(numpy.allclose(est_z, actual_z))

# -------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestPfP, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

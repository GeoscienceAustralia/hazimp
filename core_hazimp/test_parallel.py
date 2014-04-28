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
Test the parallel module.
"""
import numpy
import unittest

from core_hazimp.parallel import STATE, scatter_dict, gather_dict


class TestParallel(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parallel_off(self):
        pass

    def test_scatter_dict(self):
        # This test can be run with
        # mpirun -n 2 python test_parallel.py
        # if there is a path problem, try adding -x PYTHONPATH

        try:

            import pypar  # pylint: disable=W0612, W0404
        except ImportError:
            # can't do this test
            return
        whole = {"foo": numpy.array([0, 1, 2, 3]),
                 "woo": numpy.array([0, 10, 20, 30])}
        (subset, _) = scatter_dict(whole)
        if STATE.size == 1:
            self.assertDictEqual(whole, subset)
        elif STATE.size == 2:
            if STATE.rank == 0:
                act = {"foo": numpy.array([0, 2]),
                       "woo": numpy.array([0, 20])}
                for key in act.keys():
                    self.assertSequenceEqual(list(act[key]),
                                             list(subset[key]))
            else:
                act = {"foo": numpy.array([1, 3]),
                       "woo": numpy.array([10, 30])}
                for key in act.keys():
                    self.assertSequenceEqual(list(act[key]),
                                             list(subset[key]))
        else:
            pass

    def test_gather_dict(self):
        # This test can be run with
        # mpirun -n 2 python test_parallel.py
        # if there is a path problem, try adding -x PYTHONPATH

        try:
            import pypar  # pylint: disable=W0612, W0404
        except ImportError:
            # can't do this test
            return
        subset = {"foo": numpy.array([0, 2]),
                  "woo": numpy.array([0, 20])}

        if STATE.size == 1:
            all_indexes = [[0, 1]]
        elif STATE.size == 2:
            all_indexes = [[0, 2], [1, 3]]
        elif STATE.size == 3:
            all_indexes = [[0, 3], [1, 4], [2, 5]]
        if STATE.size < 4:
            whole = gather_dict(subset, all_indexes[STATE.rank])
        if STATE.size == 1:
            self.assertDictEqual(whole, subset)
        elif STATE.size == 2 and STATE.rank == 0:
            act = {"foo": numpy.array([0, 0, 2, 2]),
                   "woo": numpy.array([0, 0, 20, 20])}
            for key in act.keys():
                self.assertSequenceEqual(list(act[key]),
                                         list(whole[key]))
        elif STATE.size == 3 and STATE.rank == 0:
            act = {"foo": numpy.array([0, 0, 0, 2, 2, 2]),
                   "woo": numpy.array([0, 0, 0, 20, 20, 20])}
            for key in act.keys():
                self.assertSequenceEqual(list(act[key]),
                                         list(whole[key]))
        else:
            pass

    def test_gather_dict2D(self):
        # This test can be run with
        # mpirun -n 2 python test_parallel.py
        # if there is a path problem, try adding -x PYTHONPATH

        try:
            import pypar  # pylint: disable=W0612, W0404
        except ImportError:
            # can't do this test
            return
        # In a real run the subsets will not be the same
        subset = {"foo": numpy.array([0, 2]),
                  "woo": numpy.array([[1, 3, 4], [2, 4, 5]])}

        if STATE.size == 1:
            all_indexes = [[0, 1]]
        elif STATE.size == 2:
            all_indexes = [[0, 2], [1, 3]]
        elif STATE.size == 3:
            all_indexes = [[0, 3], [1, 4], [2, 5]]
        if STATE.size < 4:
            whole = gather_dict(subset, all_indexes[STATE.rank])
        if STATE.size == 1:
            self.assertDictEqual(whole, subset)
        elif STATE.size == 2 and STATE.rank == 0:
            act = {"foo": numpy.array([0, 0, 2, 2]),
                   "woo": numpy.array([[1, 3, 4], [1, 3, 4],
                                       [2, 4, 5], [2, 4, 5]])}
            for key in act.keys():
                self.assertTrue(numpy.allclose(act[key],
                                               whole[key]))
        elif STATE.size == 3 and STATE.rank == 0:
            act = {"foo": numpy.array([0, 0, 0, 2, 2, 2]),
                   "woo": numpy.array([[1, 3, 4], [1, 3, 4], [1, 3, 4],
                                       [2, 4, 5], [2, 4, 5], [2, 4, 5]])}
            for key in act.keys():
                self.assertTrue(numpy.allclose(act[key],
                                               whole[key]))
        else:
            pass

# -------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(TestParallel, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

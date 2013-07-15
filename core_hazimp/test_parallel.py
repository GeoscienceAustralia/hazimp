# -*- coding: utf-8 -*-

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

from core_hazimp.parallel import STATE, spread_dict


class TestParallel(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parallel_off(self):
        pass

    def test_parallel_on(self):
        # This test can be run with
        # mpirun -n 2 python test_parallel.py
        # if there is a path problem, try adding -x PYTHONPATH

        try:
            import pypar  # pylint: disable=W0612
        except ImportError:
            # can't do this test
            return
        whole = {"foo": numpy.array([0, 1, 2, 3]),
                 "woo": numpy.array([0, 10, 20, 30])}
        (_, subset) = spread_dict(whole)
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


#-------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(TestParallel, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

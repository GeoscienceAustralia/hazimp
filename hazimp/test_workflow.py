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
Test the workflow module.
"""

import unittest
import tempfile
import os

from scipy import allclose, asarray

from hazimp import workflow
from hazimp import context
from hazimp.calcs.calcs import CALCS
from hazimp.jobs.jobs import JOBS, LOADCSVEXPOSURE, CONSTANT
from hazimp import parallel
from hazimp import pipeline


class TestWorkFlow(unittest.TestCase):

    """
    Test the workflow module
    """

    def test_PipeLine_actually(self):

        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.csv',
                                        prefix='test_Job_title_fix_Co',
                                        delete=False)
        f.write('LAT, LONG, a_test, b_test,BUILDING\n')
        f.write('1., 2., 3., 30.,TAB\n')
        f.write('4., 5., 6., 60.,DSG\n')
        f.close()
        f2 = tempfile.NamedTemporaryFile(suffix='.csv',
                                         prefix='test_Job_title_fix_Co',
                                         delete=False)
        f2.close()
        atts = {'file_name': f.name,
                context.EX_LAT: 'LAT',
                context.EX_LONG: 'LONG'}
        caj1 = workflow.ConfigAwareJob(JOBS[LOADCSVEXPOSURE], atts_to_add=atts)

        atts = {'var': 'con_test', 'value': 'yeah'}
        caj2 = workflow.ConfigAwareJob(JOBS[CONSTANT], atts_to_add=atts)
        atts = {'var': 'con2_test', 'value': 30}
        caj3 = workflow.ConfigAwareJob(JOBS[CONSTANT], atts_to_add=atts)

        calc_list = [caj1, caj2, caj3, CALCS['add_test']]
        cont_in = context.Context()

        the_pipeline = pipeline.PipeLine(calc_list)
        the_pipeline.run(cont_in)
        cont_dict = cont_in.save_exposure_atts(f2.name)
        os.remove(f2.name)
        if parallel.STATE.rank == 0:
            self.assertTrue(allclose(cont_dict['c_test'],
                                     asarray([33., 66.])))
            self.assertEqual(cont_dict['BUILDING'].tolist(),
                             ['TAB', 'DSG'])
            self.assertTrue(allclose(cont_dict['con2_test'],
                                     asarray([30., 30.])))
            self.assertEqual(cont_dict['con_test'].tolist(),
                             ['yeah', 'yeah'])
        os.remove(f.name)

    def test_Builder(self):
        a_test = 5
        b_test = 2
        calc_list = [CALCS['add_test'], CALCS['multiply_test']]
        cont_in = context.Context()
        cont_in.exposure_att = {'a_test': a_test, 'b_test': b_test}
        the_pipeline = pipeline.PipeLine(calc_list)
        the_pipeline.run(cont_in)
        self.assertEqual(cont_in.exposure_att['d_test'], 35)

    def test_BuilderII(self):
        a_test = 5
        b_test = 2
        caj = workflow.ConfigAwareJob(CALCS['constant_test'],
                                      atts_to_add={'constant': 5})
        calc_list = [CALCS['add_test'], CALCS['multiply_test'],
                     caj]
        cont_in = context.Context()
        cont_in.exposure_att = {'a_test': a_test, 'b_test': b_test}
        the_pipeline = pipeline.PipeLine(calc_list)
        the_pipeline.run(cont_in)
        self.assertEqual(cont_in.exposure_att['d_test'], 35)
        self.assertEqual(cont_in.exposure_att['g_test'], 10)

# -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestWorkFlow, 'test')
    # Suite = unittest.makeSuite(TestWorkFlow, '')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)

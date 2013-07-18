# -*- coding: utf-8 -*-
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
import tempfile
import os
import numpy

from scipy import allclose, asarray, isnan, reshape, array

from core_hazimp.jobs.jobs import (JOBS, LOADRASTER, LOADCSVEXPOSURE,
    SAVEALL)
from core_hazimp.jobs.test_vulnerability_model import build_example
from core_hazimp.jobs import jobs
from core_hazimp import workflow
from core_hazimp import misc
from core_hazimp import parallel


class Dummy:
    """
    Dummy class for testing
    """
    def __init__(self):
        # For test_SimpleLinker
        self.vul_function_titles = {}

        # For test_SelectVulnFunction
        self.vulnerability_sets = {}
        self.exposure_att = {}


class DummyVulnSet:
    """
    Dummy class of vuln_set for testing.
    """
    def __init__(self, vuln_set):
        # For test_SimpleLinker
        self.vuln_set = vuln_set

    def build_realised_vuln_curves(self, vuln_function_ids,
                                   variability_method):
        """For test_SimpleLinker
        """

        return (vuln_function_ids,
                variability_method,
                self.vuln_set)


class TestJobs(unittest.TestCase):
    """
    Test the calcs module
    """

    def test_const_test(self):
        inst = JOBS['const_test']
        context = Dummy
        context.exposure_att = {'a_test': 5, 'b_test': 20}
        #config = {'eggs':{'c_test': 25}}
        test_kwargs = {'c_test': 25}
        inst(context, **test_kwargs)
        self.assertEqual(context.exposure_att['c_test'], 25)

    def test_load_csv_exposure(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt',
            prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, Z\n')
        f.write('1., 2., 3.\n')
        f.write('4., 5., 6.\n')
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        context = Dummy
        context.exposure_lat = None
        context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'file_name': f.name}
        inst(context, **test_kwargs)

        if parallel.STATE.size == 1:
            self.assertTrue(allclose(context.exposure_lat,
                                     asarray([1.0, 4.0])))
            self.assertTrue(allclose(context.exposure_long,
                                     asarray([2.0, 5.0])))
            self.assertTrue(allclose(context.exposure_att['Z'],
                                     asarray([3.0, 6.0])))
        else:
            if parallel.STATE.rank == 0:
                self.assertTrue(allclose(context.exposure_lat,
                                         asarray([1.0])))
                self.assertTrue(allclose(context.exposure_long,
                                         asarray([2.0])))
                self.assertTrue(allclose(context.exposure_att['Z'],
                                         asarray([3.0])))
            elif parallel.STATE.rank == 1:
                self.assertTrue(allclose(context.exposure_lat,
                                         asarray([4.0])))
                self.assertTrue(allclose(context.exposure_long,
                                         asarray([5.0])))
                self.assertTrue(allclose(context.exposure_att['Z'],
                                         asarray([6.0])))
        os.remove(f.name)

    def test_load_vuln_set(self):
        # Write a file to test
        filename = build_example()

        context = Dummy
        context.exposure_lat = None
        context.exposure_long = None
        context.vulnerability_sets = {}
        test_kwargs = {'file_name': filename}
        inst = JOBS['load_xml_vulnerability']
        inst(context, **test_kwargs)
        page = context.vulnerability_sets['PAGER']

        # This is enough of a check
        # Other tests check that it is fully loaded.
        self.assertEqual(page.asset_category, "chickens")

        os.remove(filename)

    def test_SimpleLinker(self):
        context = Dummy()
        test_kwargs = {'vul_functions_in_exposure': {'food': 100}}
        inst = JOBS[jobs.SIMPLELINKER]
        inst(context, **test_kwargs)
        actual = test_kwargs['vul_functions_in_exposure']
        self.assertDictEqual(actual, context.vul_function_titles)

    def test_SelectVulnFunction(self):
        set1 = 'Contents'
        set2 = 'Buildings'
        column1 = set1
        column2 = set2
        exp1 = ['con1', 'con2']
        exp2 = ['bld1', 'bld2']
        VulnSet1 = DummyVulnSet(set1)
        VulnSet2 = DummyVulnSet(set2)
        context = Dummy()
        context.vulnerability_sets = {set1: VulnSet1, set2: VulnSet2}
        context.vul_function_titles = {set1: column1, set2: column2}
        context.exposure_att[column1] = exp1
        context.exposure_att[column2] = exp2

        variability_method = {set1: 'mean1', set2: 'mean2'}

        test_kwargs = {'variability_method':
                       variability_method}
        inst = JOBS[jobs.SELECTVULNFUNCTION]
        inst(context, **test_kwargs)
        actual = {set1: (exp1, 'mean1', set1), set2: (exp2, 'mean2', set2)}
        self.assertDictEqual(actual, context.exposure_vuln_curves)

    def test_load_raster(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_actual\n')
        f.write('8.1, 0.1, 1, 4\n')
        f.write('7.9, 1.5, 2, -9999\n')
        f.write('8.9, 2.9, 3, 6\n')
        f.write('8.9, 3.1, 4, -9999\n')
        f.write('9.9, 2.9, 5, -9999\n')
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        context = Dummy
        context.exposure_lat = None
        context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'file_name': f.name}
        inst(context, **test_kwargs)
        os.remove(f.name)

        # Write a hazard file
        f = tempfile.NamedTemporaryFile(
            suffix='.aai', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('ncols 3    \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner +0.    \r\n')
        f.write('yllcorner +8. \r\n')
        f.write('cellsize 1    \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('1 2 -9999    \r\n')
        f.write('4 5 6 ')
        f.close()
        haz_v = 'haz_v'
        inst = JOBS[LOADRASTER]
        test_kwargs = {'file_list': [f.name], 'attribute_label': haz_v}
        inst(context, **test_kwargs)
        the_nans = isnan(context.exposure_att[haz_v])
        context.exposure_att[haz_v][the_nans] = -9999
        msg = "context.exposure_att[haz_v] " + str(context.exposure_att[haz_v])
        msg += "\n not = context.exposure_att['haz_actual'] " + \
            str(context.exposure_att['haz_actual'])
        self.assertTrue(allclose(context.exposure_att[haz_v],
                                 context.exposure_att['haz_actual']), msg)

    def test_look_up(self):
        pass
        # FIXME Needs test.

    def test_LoadCsvExposure(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_0, haz_1\n')
        f.write('8.1, 0.1, 1, 4, 40\n')
        f.write('7.9, 1.5, 2, -9999, -9999\n')
        f.write('8.9, 2.9, 3, 6, 60\n')
        f.write('8.9, 3.1, 4, -9999, -9999\n')
        f.write('9.9, 2.9, 5, -9999, -9999\n')
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        context = Dummy
        context.exposure_lat = context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'file_name': f.name}
        inst(context, **test_kwargs)

        os.remove(f.name)

        if parallel.STATE.size == 1:
            actual = numpy.arange(1, 6)
            msg = "context.exposure_att['ID'] " \
                + str(context.exposure_att['ID'])
            msg += "\n actual " + str(actual)
            self.assertTrue(allclose(context.exposure_att['ID'], actual), msg)
        else:
            if parallel.STATE.rank == 0:
                actual = numpy.array([1, 3, 5])
                msg = "context.exposure_att['ID'] " \
                    + str(context.exposure_att['ID'])
                msg += "\n actual " + str(actual)
                self.assertTrue(allclose(context.exposure_att['ID'], actual),
                                msg)
            elif parallel.STATE.rank == 1:
                actual = numpy.array([2, 4])
                msg = "context.exposure_att['ID'] " \
                    + str(context.exposure_att['ID'])
                msg += "\n actual " + str(actual)
                self.assertTrue(allclose(context.exposure_att['ID'], actual),
                                msg)

    def test_LoadCsvExposureII(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('latitude, longitude, ID, haz_0, haz_1\n')
        f.write('8.1, 0.1, 1, 4, 40\n')
        f.write('7.9, 1.5, 2, -9999, -9999\n')
        f.write('8.9, 2.9, 3, 6, 60\n')
        f.write('8.9, 3.1, 4, -9999, -9999\n')
        f.write('9.9, 2.9, 5, -9999, -9999\n')
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        context = Dummy
        context.exposure_lat = context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'exposure_latitude': 'monkey',
                       'exposure_longitude': 'eagle'}
        self.assertRaises(RuntimeError, inst, context, **test_kwargs)
        os.remove(f.name)

    def test_load_rasters(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_0, haz_1\n')
        f.write('8.1, 0.1, 1, 4, 40\n')
        f.write('7.9, 1.5, 2, -9999, -9999\n')
        f.write('8.9, 2.9, 3, 6, 60\n')
        f.write('8.9, 3.1, 4, -9999, -9999\n')
        f.write('9.9, 2.9, 5, -9999, -9999\n')
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        context = Dummy
        context.exposure_lat = context.exposure_long = None
        context.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(context, **test_kwargs)
        os.remove(f.name)

        # Write a hazard file
        f = tempfile.NamedTemporaryFile(
            suffix='.aai', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('ncols 3 \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner +0. \r\n')
        f.write('yllcorner +8. \r\n')
        f.write('cellsize 1 \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('1 2 -9999 \r\n')
        f.write('4 5 6 ')
        f.close()
        files = [f.name]

        # Write another hazard file
        f = tempfile.NamedTemporaryFile(
            suffix='.aai', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('ncols 3 \r\n')
        f.write('nrows 2 \r\n')
        f.write('xllcorner +0. \r\n')
        f.write('yllcorner +8. \r\n')
        f.write('cellsize 1 \r\n')
        f.write('NODATA_value -9999 \r\n')
        f.write('10 20 -9999 \r\n')
        f.write('40 50 60 ')
        f.close()
        files.append(f.name)

        haz_v = 'haz_v'
        inst = JOBS[LOADRASTER]
        test_kwargs = {'file_list': files, 'attribute_label': haz_v}
        inst(context, **test_kwargs)
        the_nans = isnan(context.exposure_att[haz_v])
        context.exposure_att[haz_v][the_nans] = -9999
        actual = asarray([context.exposure_att['haz_0'],
                          context.exposure_att['haz_1']])
        actual = reshape(actual, (5, 2))
        msg = "context.exposure_att[haz_av] " \
            + str(context.exposure_att[haz_v])
        msg += "\n actual " + str(actual)
        self.assertTrue(allclose(context.exposure_att[haz_v], actual), msg)

        for a_file in files:
            os.remove(a_file)

    def test_save_exposure(self):
        # get a file name
        f = tempfile.NamedTemporaryFile(
            suffix='.npz',
            prefix='HAZIMPt_jobs_test_save_exposure',
            delete=False)
        f.close()

        inst = JOBS[SAVEALL]
        con = workflow.Context()
        actual = {'shoes': array([11., 11]),
                  'depth': array([[5., 3.], [2., 4]]),
                  misc.INTID: array([0, 1, 2])}
        con.exposure_att = actual
        lat = array([1, 22.])
        con.exposure_lat = lat
        lon = array([100., 22.])
        con.exposure_long = lon
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(con, **test_kwargs)

        exp_dict = numpy.load(f.name)

        actual[workflow.EX_LONG] = lon
        actual[workflow.EX_LAT] = lat
        for the_key in exp_dict.files:
            self.assertTrue(allclose(exp_dict[the_key],
                                     actual[the_key]))
        os.remove(f.name)

#-------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestJobs, 'test')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

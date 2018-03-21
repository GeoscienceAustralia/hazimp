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
import tempfile
import os
import numpy

from scipy import allclose, asarray, isnan, array, rollaxis

from core_hazimp.jobs.jobs import (JOBS, LOADRASTER, LOADCSVEXPOSURE,
                                   SAVEALL, CONSTANT, ADD, RANDOM_CONSTANT,
                                   MULT, MDMULT)
from core_hazimp.jobs.test_vulnerability_model import build_example
from core_hazimp.jobs import jobs
from core_hazimp import context
from core_hazimp import misc
from core_hazimp import parallel


class Dummy(object):

    """
    Dummy class for testing
    """

    def __init__(self, site_shape=None):
        # For test_SimpleLinker
        self.vul_function_titles = {}

        # For test_SelectVulnFunction
        self.vulnerability_sets = {}
        self.exposure_att = {}
        self.site_shape = site_shape

    def get_site_shape(self):
        """ Return the number of sites"""
        return self.site_shape


class DummyVulnSet(object):

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
        con_in = Dummy(site_shape=(1,))
        con_in.exposure_att = {'a_test': 5, 'b_test': 20}
        test_kwargs = {'c_test': 25}
        inst(con_in, **test_kwargs)
        self.assertEqual(con_in.exposure_att['c_test'], 25)

    def test_const(self):
        inst = JOBS[CONSTANT]
        con_in = Dummy(site_shape=(1,))
        con_in.exposure_att = {'a_test': 5, 'b_test': 20}
        test_kwargs = {'var': 'c_test', 'value': 25}
        inst(con_in, **test_kwargs)
        self.assertEqual(con_in.exposure_att['c_test'], 25)

    def test_const2(self):
        inst = JOBS[CONSTANT]
        con_in = Dummy(site_shape=(1,))
        con_in.exposure_att = {'a_test': 5, 'b_test': 20}
        test_kwargs = {'var': 'c_test', 'value': 'yeah'}
        inst(con_in, **test_kwargs)
        self.assertEqual(con_in.exposure_att['c_test'], 'yeah')

    def test_const3(self):
        inst = JOBS[CONSTANT]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'a_test': numpy.array([25, 20]),
                               'b_test': numpy.array([2, 40])}
        test_kwargs = {'var': 'c_test', 'value': 35}
        inst(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([35, 35])))

    def test_const4(self):
        # Just make sure it does the adding right.
        inst = JOBS[CONSTANT]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'a_test': numpy.array([25, 20]),
                               'b_test': numpy.array([2, 40])}
        test_kwargs = {'var': 'c_test', 'value': 'yeah'}
        inst(con_in, **test_kwargs)
        # print "con_in.exposure_att['c_test']", con_in.exposure_att['c_test']
        # This fails
        self.assertEqual(con_in.exposure_att['c_test'].tolist(),
                         ['yeah', 'yeah'])

    def test_rand_const(self):
        inst = JOBS[RANDOM_CONSTANT]
        con_in = Dummy(site_shape=(5,))
        values = {1: 0.2, 2: 0.5, 3: 0.3}
        forced_random = numpy.array([0.19, 0.21, 0.69, 0.71, 0.99])
        test_kwargs = {'var': 'test', 'values': values,
                       'forced_random': forced_random}
        inst(con_in, **test_kwargs)
        actual = [1, 2, 2, 3, 3]
        self.assertEqual(con_in.exposure_att['test'].tolist(),
                         actual)

    def test_rand_const2(self):
        inst = JOBS[RANDOM_CONSTANT]
        con_in = Dummy(site_shape=(5,))
        values = {'a': 0.2, 'b': 0.5, 'c': 0.3}
        forced_random = numpy.array([0.19, 0.21, 0.69, 0.71, 0.99])
        test_kwargs = {'var': 'test', 'values': values,
                       'forced_random': forced_random}
        inst(con_in, **test_kwargs)
        actual = ['a', 'b', 'b', 'c', 'c']
        self.assertEqual(con_in.exposure_att['test'].tolist(),
                         actual)

    def test_rand_const3(self):
        inst = JOBS[RANDOM_CONSTANT]
        con_in = Dummy(site_shape=(5,))
        values = {'c': 0.2, 'b': 0.5, 'a': 0.3}
        forced_random = numpy.array([0.29, 0.31, 0.79, 0.81, 0.99])
        test_kwargs = {'var': 'test', 'values': values,
                       'forced_random': forced_random}
        inst(con_in, **test_kwargs)
        actual = ['a', 'b', 'b', 'c', 'c']
        self.assertEqual(con_in.exposure_att['test'].tolist(),
                         actual)

    def test_rand_const4(self):
        inst = JOBS[RANDOM_CONSTANT]
        con_in = Dummy(site_shape=(5,))
        values = {'c': 0.2, 'b': 0.5, 'a': 0.3}
        forced_random = numpy.array([0.29, 0.31, 0.79, 0.81, 0.99])
        forced_random = numpy.array([0.99, 0.81, 0.79, 0.31, 0.29])
        test_kwargs = {'var': 'test', 'values': values,
                       'forced_random': forced_random}
        inst(con_in, **test_kwargs)
        actual = ['c', 'c', 'b', 'b', 'a']
        self.assertEqual(con_in.exposure_att['test'].tolist(),
                         actual)

    def test_add(self):
        inst_const = JOBS[CONSTANT]
        inst_add = JOBS[ADD]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'b_test': numpy.array([2, 40])}
        test_kwargs = {'var': 'a_test', 'value': 20}
        inst_const(con_in, **test_kwargs)
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([22, 60])))

    def test_addII(self):
        inst_const = JOBS[CONSTANT]
        inst_add = JOBS[ADD]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'b_test': numpy.array(['_time', '_drinks'])}
        test_kwargs = {'var': 'a_test', 'value': 'summer'}
        inst_const(con_in, **test_kwargs)
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertEqual(con_in.exposure_att['c_test'].tolist(),
                         ['summer_time', 'summer_drinks'])

    def test_addIII(self):
        inst_const = JOBS[CONSTANT]
        inst_add = JOBS[ADD]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'b_col': numpy.array(['_summer', '_winter']),
                               'c_col': numpy.array(['_time', '_meals'])}
        test_kwargs = {'var': 'a_col', 'value': 'more'}
        inst_const(con_in, **test_kwargs)
        test_kwargs = {'var1': 'b_col', 'var2': 'c_col', 'var_out': 'd_col'}
        inst_add(con_in, **test_kwargs)
        test_kwargs = {'var1': 'a_col', 'var2': 'd_col', 'var_out': 'answer'}
        inst_add(con_in, **test_kwargs)
        self.assertEqual(con_in.exposure_att['answer'].tolist(),
                         ['more_summer_time', 'more_winter_meals'])

    def test_Mult(self):
        inst_const = JOBS[CONSTANT]
        inst_add = JOBS[MULT]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'b_test': numpy.array([2, 40])}
        test_kwargs = {'var': 'a_test', 'value': 20}
        inst_const(con_in, **test_kwargs)
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([40, 800])))

    def test_MultII(self):
        inst_add = JOBS[MULT]
        con_in = Dummy(site_shape=(2,))
        con_in.exposure_att = {'a_test':
                               numpy.array([2, 4]),
                               'b_test': numpy.array([3, 8])}
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([6, 32])))

    def test_MultIII(self):
        inst_add = JOBS[MULT]
        con_in = Dummy(site_shape=(2, 2))
        con_in.exposure_att = {'a_test':
                               numpy.array([[2, 4], [1, 2]]),
                               'b_test': numpy.array([3, 10])}
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([[6, 40], [3, 20]])))

    def test_MultIV(self):
        inst_add = JOBS[MULT]
        con_in = Dummy(site_shape=(2, 2))
        con_in.exposure_att = {'a_test':
                               numpy.array([3, 10]),
                               'b_test': numpy.array([[2, 4], [1, 2], [1, 2]])}
        test_kwargs = {'var1': 'a_test', 'var2': 'b_test', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([[6, 40], [3, 20], [3, 20]])))

    def test_MDMult(self):
        # site is D0 for var1 and var2
        inst_add = JOBS[MDMULT]
        con_in = Dummy(site_shape=(2, 2))
        con_in.exposure_att = {'var2':
                               numpy.array([3, 10, 1]),
                               'var1': numpy.array([[2, 4], [1, 2], [1, 2]])}
        test_kwargs = {'var1': 'var1', 'var2': 'var2', 'var_out': 'c_test'}
        inst_add(con_in, **test_kwargs)
        self.assertTrue(allclose(con_in.exposure_att['c_test'],
                                 asarray([[6, 12], [10, 20], [1, 2]])))

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
        con_in = Dummy()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = None
        test_kwargs = {'file_name': f.name}
        inst(con_in, **test_kwargs)

        if parallel.STATE.size == 1:
            self.assertTrue(allclose(con_in.exposure_lat,
                                     asarray([1.0, 4.0])))
            self.assertTrue(allclose(con_in.exposure_long,
                                     asarray([2.0, 5.0])))
            self.assertTrue(allclose(con_in.exposure_att['Z'],
                                     asarray([3.0, 6.0])))
        else:
            if parallel.STATE.rank == 0:
                self.assertTrue(allclose(con_in.exposure_lat,
                                         asarray([1.0])))
                self.assertTrue(allclose(con_in.exposure_long,
                                         asarray([2.0])))
                self.assertTrue(allclose(con_in.exposure_att['Z'],
                                         asarray([3.0])))
            elif parallel.STATE.rank == 1:
                self.assertTrue(allclose(con_in.exposure_lat,
                                         asarray([4.0])))
                self.assertTrue(allclose(con_in.exposure_long,
                                         asarray([5.0])))
                self.assertTrue(allclose(con_in.exposure_att['Z'],
                                         asarray([6.0])))
        os.remove(f.name)

    def test_load_vuln_set(self):
        # Write a file to test
        filename = build_example()

        con_in = Dummy()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.vulnerability_sets = {}
        test_kwargs = {'file_name': filename}
        inst = JOBS['load_xml_vulnerability']
        inst(con_in, **test_kwargs)
        page = con_in.vulnerability_sets['PAGER']

        # This is enough of a check
        # Other tests check that it is fully loaded.
        self.assertEqual(page.asset_category, "chickens")

        os.remove(filename)

    def test_SimpleLinker(self):
        con_in = Dummy()
        test_kwargs = {'vul_functions_in_exposure': {'food': 100}}
        inst = JOBS[jobs.SIMPLELINKER]
        inst(con_in, **test_kwargs)
        actual = test_kwargs['vul_functions_in_exposure']
        self.assertDictEqual(actual, con_in.vul_function_titles)

    def test_SelectVulnFunction(self):
        set1 = 'Contents'
        set2 = 'Buildings'
        column1 = set1
        column2 = set2
        exp1 = ['con1', 'con2']
        exp2 = ['bld1', 'bld2']
        VulnSet1 = DummyVulnSet(set1)
        VulnSet2 = DummyVulnSet(set2)
        con_in = Dummy()
        con_in.vulnerability_sets = {set1: VulnSet1, set2: VulnSet2}
        con_in.vul_function_titles = {set1: column1, set2: column2}
        con_in.exposure_att[column1] = exp1
        con_in.exposure_att[column2] = exp2

        variability_method = {set1: 'mean1', set2: 'mean2'}

        test_kwargs = {'variability_method':
                       variability_method}
        inst = JOBS[jobs.SELECTVULNFUNCTION]
        inst(con_in, **test_kwargs)
        actual = {set1: (exp1, 'mean1', set1), set2: (exp2, 'mean2', set2)}
        self.assertDictEqual(actual, con_in.exposure_vuln_curves)

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
        con_in = context.Context()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name}
        inst(con_in, **test_kwargs)
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
        inst(con_in, **test_kwargs)
        the_nans = isnan(con_in.exposure_att[haz_v])
        con_in.exposure_att.loc[the_nans, (haz_v,)] = -9999
        msg = "con_in.exposure_att[haz_v] " + str(con_in.exposure_att[haz_v])
        msg += "\n not = con_in.exposure_att['haz_actual'] " + \
            str(con_in.exposure_att['haz_actual'])
        self.assertTrue(allclose(con_in.exposure_att[haz_v],
                                 con_in.exposure_att['haz_actual']), msg)
        os.remove(f.name)
    @unittest.skip("Failing comparison of NaN values")
    def test_load_raster_clipping(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_actual\n')
        f.write('8.1, 0.1, 1, 4\n')
        f.write('7.9, 1.5, 2, -9999\n')  # Out of Haz area
        f.write('8.9, 2.9, 3, 6\n')
        f.write('8.9, 3.1, 4, -9999.\n')  # Out of Haz area
        f.write('9.9, 2.9, 5, NaN\n')  # In no data area
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        con_in = context.Context()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(con_in, **test_kwargs)
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
        f.write('NODATA_value -9999\r\n')
        f.write('1 2 -9999    \r\n')
        f.write('4 5 6 ')
        f.close()
        haz_v = 'haz_v'
        inst = JOBS[LOADRASTER]
        test_kwargs = {'file_list': [f.name], 'attribute_label': haz_v,
                       'clip_exposure2all_hazards': True}
        inst(con_in, **test_kwargs)
        the_nans = isnan(con_in.exposure_att[haz_v])
        
        con_in.exposure_att.loc[the_nans, (haz_v,)] = numpy.NAN#-9999
        msg = "con_in.exposure_att[haz_v] \n" + str(con_in.exposure_att[haz_v].values)
        msg += "\n not = con_in.exposure_att['haz_actual'] \n" + \
            str(con_in.exposure_att['haz_actual'].values)
        self.assertTrue(allclose(con_in.exposure_att[haz_v].values,
                                 con_in.exposure_att['haz_actual'].values), msg)
        # There should be only 3 exposure points
        expected = 3
        msg = "Number of exposure points is "
        msg += str(len(con_in.exposure_att['ID']))
        msg += "\n Expected " + str(expected)
        self.assertTrue(len(con_in.exposure_att['ID']) == expected, msg)
        os.remove(f.name)

    def test_load_raster_clippingII(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_actual\n')
        f.write('7.9, 1.5, 2, -9999\n')  # Out of Haz area
        f.write('8.9, 3.1, 4, -9999\n')  # Out of Haz area
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        con_in = context.Context()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(con_in, **test_kwargs)
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
        test_kwargs = {'file_list': [f.name], 'attribute_label': haz_v,
                       'clip_exposure2all_hazards': True}
        inst(con_in, **test_kwargs)

        # There should be only no exposure points
        expected = 0
        msg = "Number of exposure points is "
        msg += str(len(con_in.exposure_att['ID']))
        msg += "\n Expected " + str(expected)
        self.assertTrue(len(con_in.exposure_att['ID']) == expected, msg)
        os.remove(f.name)

    def test_load_raster_clippingIII(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(
            suffix='.txt', prefix='HAZIMPtest_jobs',
            delete=False)
        f.write('exposure_latitude, exposure_longitude, ID, haz_actual\n')
        f.write('7.9, 1.5, 2, -9999\n')  # Out of Haz area
        f.write('8.9, 3.1, 4, -9999\n')  # Out of Haz area
        f.close()

        inst = JOBS[LOADCSVEXPOSURE]
        con_in = context.Context()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(con_in, **test_kwargs)
        os.remove(f.name)

        raster = array([[1, 2, -9999], [4, 5, 6]])
        upper_left_x = 0
        upper_left_y = 10
        cell_size = 1
        no_data_value = -9999
        haz_v = 'haz_v'
        inst = JOBS[LOADRASTER]
        test_kwargs = {'attribute_label': haz_v,
                       'clip_exposure2all_hazards': True,
                       'raster': raster,
                       'upper_left_x': upper_left_x,
                       'upper_left_y': upper_left_y,
                       'cell_size': cell_size,
                       'no_data_value': no_data_value}
        inst(con_in, **test_kwargs)

        # There should be only no exposure points
        expected = 0
        msg = "Number of exposure points is "
        msg += str(len(con_in.exposure_att['ID']))
        msg += "\n Expected " + str(expected)
        self.assertTrue(len(con_in.exposure_att['ID']) == expected, msg)

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
        con_in = context.Context()
        con_in.exposure_lat = None
        con_in.exposure_long = None
        con_in.exposure_att = None
        test_kwargs = {'file_name': f.name}
        inst(con_in, **test_kwargs)

        os.remove(f.name)

        if parallel.STATE.size == 1:
            actual = numpy.arange(1, 6)
            msg = "con_in.exposure_att['ID'] " \
                + str(con_in.exposure_att['ID'])
            msg += "\n actual " + str(actual)
            self.assertTrue(allclose(con_in.exposure_att['ID'], actual), msg)
        else:
            if parallel.STATE.rank == 0:
                actual = numpy.array([1, 3, 5])
                msg = "con_in.exposure_att['ID'] " \
                    + str(con_in.exposure_att['ID'])
                msg += "\n actual " + str(actual)
                self.assertTrue(allclose(con_in.exposure_att['ID'], actual),
                                msg)
            elif parallel.STATE.rank == 1:
                actual = numpy.array([2, 4])
                msg = "con_in.exposure_att['ID'] " \
                    + str(con_in.exposure_att['ID'])
                msg += "\n actual " + str(actual)
                self.assertTrue(allclose(con_in.exposure_att['ID'], actual),
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
        con_in = Dummy
        con_in.exposure_lat = con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'exposure_latitude': 'monkey',
                       'exposure_longitude': 'eagle'}
        self.assertRaises(RuntimeError, inst, con_in, **test_kwargs)
        os.remove(f.name)

    @unittest.skip("Skip test of loading multiple rasters")
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
        con_in = context.Context()
        con_in.exposure_lat = con_in.exposure_long = None
        con_in.exposure_att = {}
        test_kwargs = {'file_name': f.name, 'use_parallel': False}
        inst(con_in, **test_kwargs)
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
        inst(con_in, **test_kwargs)
        the_nans = isnan(con_in.exposure_att[haz_v])
        con_in.exposure_att[haz_v][the_nans] = -9999
        actual = asarray([con_in.exposure_att['haz_0'],
                          con_in.exposure_att['haz_1']])
        actual = rollaxis(actual, 1)
        msg = "con_in.exposure_att[haz_av] " \
            + str(con_in.exposure_att[haz_v])
        msg += "\n actual " + str(actual)
        self.assertTrue(allclose(con_in.exposure_att[haz_v], actual), msg)

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
        con = context.Context()
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

        with numpy.load(f.name) as exp_dict:
            actual[context.EX_LONG] = lon
            actual[context.EX_LAT] = lat
            for the_key in exp_dict.files:
                self.assertTrue(allclose(exp_dict[the_key],
                                         actual[the_key]))
        os.remove(f.name)

# -------------------------------------------------------------
if __name__ == "__main__":
    SUITE = unittest.makeSuite(TestJobs, 'test')
    # SUITE = unittest.makeSuite(TestJobs, 'test_load_raster_clipping')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)

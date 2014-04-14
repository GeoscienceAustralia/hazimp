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

"""
A collection of jobs to put into the pipeline.
Jobs know about the context instance.
The
initial jobs will be for setting up the calculations, such as loading
the exposure data.

And key, value pairs that are in the config file are passed to the
jobs function.  The function name is used to determine what to pass in.


Special named parameters -

file_name  - THE attribute used to describe files to load. If the file
is not present Error out. This is checked in the validate job.

file_list - THE attribute used to describe a list of files. If any file
is not present Error out.

"""

import sys
from scipy import asarray

from core_hazimp import parallel
from core_hazimp import misc
from core_hazimp import raster as raster_module
from core_hazimp.context import EX_LAT, EX_LONG
from core_hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file

ADD = 'add'
CONSTANT = 'constant'
LOADCSVEXPOSURE = 'load_exposure'
LOADRASTER = 'load_raster'
LOADXMLVULNERABILITY = 'load_xml_vulnerability'
SIMPLELINKER = 'simple_linker'
SELECTVULNFUNCTION = 'select_vulnerability_functions'
LOOKUP = 'look_up'
SAVEALL = 'save_all'
VALIDATECONFIG = 'validate_config'
JOBSKEY = 'jobs'
CELLJOIN = 'cell_join'


class Job(object):

    """
    Abstract Jobs class. Should use abc then.
    """

    def __init__(self):
        """
        Initalise a Job object having the attributes
         allargspec_call and args_in.
        """
        self.call_funct = None

    def get_call_funct(self):
        """
        Return the 'user' name for the function
        """
        return self.call_funct

    def get_required_args_no_context(self):
        """
        Get the arguments and default arguments of the job function.

        Any context parameter will be ignored.

        Returns
           args - the arguments of the job function.
           defaults - the default arguments of the job function.
        """
        args, defaults = misc.get_required_args(self.__call__)
        try:
            args.remove('context')
        except KeyError:
            pass
        try:
            args.remove('self')
        except KeyError:
            pass

        return args, defaults


class ConstTest(Job):

    """
    Simple test class. Moving a config value to the context.
    """

    def __init__(self):
        super(ConstTest, self).__init__()
        self.call_funct = 'const_test'

    def __call__(self, context, c_test=None):
        """
        A dummy job for testing.

        :param context: The context instance, used to move data around.
        :param c_test: Variable to add to context.
        """
        context.exposure_att['c_test'] = c_test


class Const(Job):

    """
    Given a key and a constant value, insert a vector of the value.
    """

    def __init__(self):
        super(Const, self).__init__()
        self.call_funct = CONSTANT

    def __call__(self, context, var, value):
        """
        A dummy job for testing.

        :param context: The context instance, used to move data around.
        :param var: Variable to add to context.
        :param value: Value of the variable added.
        """
        context.exposure_att[var] = value


class Add(Job):

    """
    Given a key and a constant value, insert a vector of the value.
    """

    def __init__(self):
        super(Add, self).__init__()
        self.call_funct = ADD

    def __call__(self, context, var1, var2, var_out):
        """
        Add two columns together, put the answer in a second column.

        :param context: The context instance, used to move data around.
        :param var1: The values in this column are added.
        :param var2: The values in this column are added.
        :param var_out: The new column name, with the values of Var1 + var2.
        """
        context.exposure_att[var_out] = misc.add(context.exposure_att[var1],
                                                 context.exposure_att[var2])


class LoadCsvExposure(Job):

    """
    Read a csv exposure file into the context object.
    """

    def __init__(self):
        super(LoadCsvExposure, self).__init__()
        self.call_funct = LOADCSVEXPOSURE

    def __call__(self, context, file_name, exposure_latitude=None,
                 exposure_longitude=None, use_parallel=True):
        """
        Read a csv exposure file into the context object.

        :param context: The context instance, used to move data around.
        :param file_name: The csv file to load.
        :param exposure_latitude: the title string of the latitude column.
        :param exposure_longitud: the title string of the longitude column.

        Content return:
            exposure_att: Add the file values into this dictionary.
            key: column titles
            value: column values, except the title
        """
        file_dict = parallel.csv2dict(file_name, use_parallel=use_parallel)

        # FIXME Need to do better error handling

        if exposure_latitude is None:
            lat_key = EX_LAT
        else:
            lat_key = exposure_latitude

        try:
            context.exposure_lat = asarray(file_dict[lat_key])
            del file_dict[lat_key]
        except KeyError:
            msg = "No Exposure latitude column labelled '%s'." % lat_key
            raise RuntimeError(msg)

        if exposure_latitude is None:
            long_key = EX_LONG
        else:
            long_key = exposure_longitude

        try:
            context.exposure_long = asarray(file_dict[long_key])
            del file_dict[long_key]
        except KeyError:
            msg = "No Exposure longitude column labelled '%s'." % long_key
            raise RuntimeError(msg)

        for key in file_dict:
            context.exposure_att[key] = asarray(file_dict[key])


class LoadXmlVulnerability(Job):

    """
    Read the vulnerability sets into the context object.
    """

    def __init__(self):
        super(LoadXmlVulnerability, self).__init__()
        self.call_funct = LOADXMLVULNERABILITY

    def __call__(self, context, file_name):
        """
        Read a csv exposure file into the context object.

        :param context: The context instance, used to move data around.
        :param file_name: The xml file to load.
        """
        if file_name is not None:
            vuln_sets = vuln_sets_from_xml_file(file_name)
            context.vulnerability_sets.update(vuln_sets)


class SimpleLinker(Job):

    """
    Link a list of vulnerability functions to each asset, given the
    vulnerability_sets and exposure columns that represents the
    vulnerability function id.
    """

    def __init__(self):
        super(SimpleLinker, self).__init__()
        self.call_funct = SIMPLELINKER

    def __call__(self, context, vul_functions_in_exposure):
        """
        Link a list of vulnerability functions to each asset, given the
        vulnerability_sets and exposure columns that represents the
        vulnerability function id.

        :param context: The context instance, used to move data around.
        :param vul_functions_in_exposure: A dictionary with keys being
        vulnerability_set_ids and values being the exposure title that
        holds vulnerability function ID's.

        Content return:
           vul_function_titles: Add's the exposure_titles
        """
        context.vul_function_titles.update(vul_functions_in_exposure)


class SelectVulnFunction(Job):

    """
    Produce vulnerability curves for each asset, given the
    vulnerability_sets and exposure columns that represents the
    vulnerability function id.

    From the vulnerability set and a function id you get the
    vulnerability function.
    Then, using the variability_method e.g. 'mean' you get the
    vulnerability curve.
    """

    def __init__(self):
        super(SelectVulnFunction, self).__init__()
        self.call_funct = SELECTVULNFUNCTION

    def __call__(self, context, variability_method=None):
        """
        Specifies what vulnerability sets to use.
        Links vulnerability curves to assets.
        Assumes the necessary vulnerability_sets have been loaded and
        there is an  exposure column that represents the
        vulnerability function id.

        NOTE: This is where the vulnerability function is selected,
            As well as sampled.

        Args:
        :param context: The context instance, used to move data around.
        :param variability_method: The vulnerability sets that will be
            looked up and the sampling method used for each set.
            A dictionary with keys being
            vulnerability_set_ids and values being the sampling method
            to generate a vulnerability curve from a vulnerability function.
            e.g. {'EQ_contents': 'mean', 'EQ_building': 'mean'}
            Limitation: A vulnerability set can only be used once, since
            it needs a unique name.

        Content return:
           exposure_vuln_curves: A dictionary of realised
               vulnerability curves, associated with the exposure
               data.
           key - intensity measure
           value - realised vulnerability curve instance per asset
        """
        exposure_vuln_curves = {}
        for vuln_set_key in variability_method:
            # Get the vulnerability set
            vuln_set = context.vulnerability_sets[vuln_set_key]
            # Get the column of function ID's
            exposure_title = context.vul_function_titles[vuln_set_key]
            vuln_function_ids = context.exposure_att[exposure_title]
            # sample from the function to get the curve
            realised_vuln_curves = vuln_set.build_realised_vuln_curves(
                vuln_function_ids,
                variability_method=variability_method[vuln_set_key])
            # Build a dictionary of realised vulnerability curves
            exposure_vuln_curves[vuln_set_key] = realised_vuln_curves

        context.exposure_vuln_curves = exposure_vuln_curves


class LookUp(Job):

    """
    Do a lookup on all the vulnerability curves, returning the
        associated loss.
    """

    def __init__(self):
        super(LookUp, self).__init__()
        self.call_funct = LOOKUP

    def __call__(self, context):
        """
        Does a look up on all the vulnerability curves, returning the
        associated loss.

        :param context: The context instance, used to move data around.

        Content return:
           exposure_vuln_curves: A dictionary of realised
               vulnerability curves, associated with the exposure
               data.
                key - intensity measure
                value - realised vulnerability curve instance per asset
        """

        for intensity_key in context.exposure_vuln_curves:
            vuln_curve = context.exposure_vuln_curves[intensity_key]
            int_measure = vuln_curve.intensity_measure_type
            loss_category_type = vuln_curve.loss_category_type
            try:
                intensities = context.exposure_att[int_measure]
            except KeyError:
                vulnerability_set_id = vuln_curve.vulnerability_set_id
                msg = 'Invalid intensity measure, %s. \n' % int_measure
                msg += 'vulnerability_set_id is %s. \n' % vulnerability_set_id
                raise RuntimeError(msg)
            losses = vuln_curve.look_up(intensities)
            context.exposure_att[loss_category_type] = losses


class LoadRaster(Job):

    """
    Load one or more files and get the value for all the
    points. Primarily this will be used to load hazard data.

    There may be NAN values in this data
    """

    def __init__(self):
        super(LoadRaster, self).__init__()
        self.call_funct = LOADRASTER

    # R0913:326: Too many arguments (9/6)
    # pylint: disable=R0913
    def __call__(self, context, attribute_label,
                 clip_exposure2all_hazards=False,
                 file_list=None,
                 raster=None, upper_left_x=None, upper_left_y=None,
                 cell_size=None, no_data_value=None):
        """
        Load one or more files and get the value for all the
        exposure points. All files have to be of the same attribute.
        Alternatively a numeric array of the raster data can be passed in.

        :param context: The context instance, used to move data around.
        :param attribute_label: The string to be associated with this data.
        :param clip_exposure2all_hazards: True if the exposure data is
            clippped to the hazard data, so no hazard values are ignored.

        :param file_list: A list of files or a single file to be loaded.
        OR
        :param raster: A 2D numeric array of the raster values, North is up.
        :param upper_left_x: The longitude at the upper left corner.
        :param upper_left_y: The latitude at the upper left corner.
        :param cell_size: The cell size.
        :param no_data_value: Values in the raster that represent no data.


        Context return:
           exposure_att: Add the file values into this dictionary.
               key: column titles
               value: column values, except the title
        """

        # We need a file or a full set of raster info.
        if file_list is None:
            # The raster info is being passed as an array
            assert raster is not None
            assert upper_left_x is not None
            assert upper_left_y is not None
            assert cell_size is not None
            assert no_data_value is not None
            a_raster = raster_module.Raster.from_array(raster, upper_left_x,
                                                       upper_left_y,
                                                       cell_size,
                                                       no_data_value)

            if clip_exposure2all_hazards:
                # Reduce the context to the hazard area
                # before the raster info has been added to the context
                extent = a_raster.extent()
                context.clip_exposure(*extent)

            file_data = a_raster.raster_data_at_points(
                context.exposure_long,
                context.exposure_lat)
            context.exposure_att[attribute_label] = file_data
        else:
            if isinstance(file_list, basestring):
                file_list = [file_list]
            file_data, extent = raster_module.files_raster_data_at_points(
                context.exposure_long,
                context.exposure_lat, file_list)
            context.exposure_att[attribute_label] = file_data

            if clip_exposure2all_hazards:
                # Clipping the exposure points after the data has been added.
                # Not optimised for speed, but easy to implement.
                context.clip_exposure(*extent)


class SaveExposure(Job):

    """
    Save all of the exposure information in the context.
    """

    def __init__(self):
        super(SaveExposure, self).__init__()
        self.call_funct = SAVEALL

    def __call__(self, context, file_name=None, use_parallel=True):
        """
        Save all of the exposure information in the context.

        :param context: The context instance, used to move data around.
        :params file_name: The file where the expsoure data will go.
        """
        context.save_exposure_atts(file_name, use_parallel=use_parallel)


# ____________________________________________________
# ----------------------------------------------------
#                KEEP THIS AT THE END
# ____________________________________________________

JOBS = misc.instanciate_classes(sys.modules[__name__])

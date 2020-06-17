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
The initial jobs will be for setting up the calculations, such as loading
the exposure data.

And key, value pairs that are in the config file are passed to the
jobs function.  The function name is used to determine what to pass in.


Special named parameters -

file_name  - THE attribute used to describe files to load. If the file
is not present Error out. This is checked in the validate job.

file_list - THE attribute used to describe a list of files. If any file
is not present Error out.

"""

import os
import re
import sys
import scipy
import pandas as pd
import numpy as np

from prov.dot import prov_to_dot

from hazimp import parallel
from hazimp import misc
from hazimp import raster as raster_module
from hazimp.context import EX_LAT, EX_LONG
from hazimp.jobs.vulnerability_model import vuln_sets_from_xml_file

ADD = 'add'
MULT = 'mult'
MDMULT = 'MultipleDimensionMult'
CONSTANT = 'constant'
LOADCSVEXPOSURE = 'load_exposure'
LOADRASTER = 'load_raster'
LOADXMLVULNERABILITY = 'load_xml_vulnerability'
SIMPLELINKER = 'simple_linker'
SELECTVULNFUNCTION = 'select_vulnerability_functions'
LOOKUP = 'look_up'
SAVEALL = 'save_all'
SAVEAGG = 'save_agg'
VALIDATECONFIG = 'validate_config'
CELLJOIN = 'cell_join'
RANDOM_CONSTANT = 'random_constant'
PERMUTATE_EXPOSURE = 'permutate_exposure'
AGGREGATE_LOSS = 'aggregate_loss'
AGGREGATE = 'aggregate'
SAVEPROVENANCE = 'saveprovenance'

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
        Given a key and a constant value, insert a vector of the value.

        :param context: The context instance, used to move data around.
        :param var: Variable to add to context.
        :param value: Value of the variable added.
        """
        shape = context.get_site_shape()
        # This uses a lot of memory,
        # but it keeps the context instance simple.
        context.exposure_att[var] = scipy.tile(scipy.asarray(value), shape)


class RandomConst(Job):

    """
    Given a key and a dictionary of values with an associated probability
    probabilistically assign a value to each element in the array.
    """

    def __init__(self):
        super(RandomConst, self).__init__()
        self.call_funct = RANDOM_CONSTANT

    def __call__(self, context, var, values, forced_random=None):
        """
        A dummy job for testing.

        :param context: The context instance, used to move data around.
        :param var: Variable to add to context.
        :param values: Value of the variable added.
        :param forced_random: Used for testing.  A vector or value to be used
                as the random numbers.
        """
        shape = context.get_site_shape()
        s_keys, s_probs = misc.sorted_dict_values(values)
        s_probs = scipy.asarray(s_probs)
        s_keys = scipy.asarray(s_keys)
        values_array = misc.weighted_values(s_keys, s_probs, shape,
                                            forced_random=forced_random)

        context.exposure_att[var] = values_array


class Add(Job):

    """
    Add two columns together, put the answer in a new column.
    """

    def __init__(self):
        super(Add, self).__init__()
        self.call_funct = ADD

    def __call__(self, context, var1, var2, var_out):
        """
        Add two columns together, put the answer in a new column.

        :param context: The context instance, used to move data around.
        :param var1: The values in this column are added.
        :param var2: The values in this column are added.
        :param var_out: The new column name, with the values of var1 + var2.
        """
        context.exposure_att[var_out] = misc.add(context.exposure_att[var1],
                                                 context.exposure_att[var2])


class Mult(Job):

    """
    Multiply two columns together, put the answer in a new column.
    """

    def __init__(self):
        super(Mult, self).__init__()
        self.call_funct = MULT

    def __call__(self, context, var1, var2, var_out):
        """
        Multiply two arrays together, put the answer in a new array.

        :param context: The context instance, used to move data around.
        :param var1: The values in this column are Multiplied.
        :param var2: The values in this column are Multiplied.
        :param var_out: The new column name, with the values of var1 * var2.
        """
        context.exposure_att[var_out] = (context.exposure_att[var1] *
                                         context.exposure_att[var2])


class MultipleDimensionMult(Job):

    """
    Multiply two arrays together, put the answer in a new array.

    Var1 has assets in the 0 dimension, and can have other dimensions.
    Var2 has the asserts in the 0 dimension and has only this dimension.
    """

    def __init__(self):
        super(MultipleDimensionMult, self).__init__()
        self.call_funct = MDMULT

    def __call__(self, context, var1, var2, var_out):
        """
        Multiply two columns together, put the answer in a new column.

        :param context: The context instance, used to move data around.
        :param var1: Variable name of data.  Usually intensity.
            Assets is the 0 dimension, and can have other dimensions.
        :param var2: The values in this column are Multiplied.
            Asserts is the 0 dimension and has only this dimension.
        :param var_out: The new variable name, with the values of
            var1 * var2.
        """
        # print "var1 ", context.exposure_att[var1].shape

        rolled = context.exposure_att[var1]
        context.exposure_att[var1] = scipy.rollaxis(rolled, 0,
                                                    rolled.ndim)
        # print "var1 rolled", context.exposure_att[var1].shape
        # print "var2", context.exposure_att[var2].shape
        # print "rolled", rolled.shape
        context.exposure_att[var_out] = (context.exposure_att[var1] *
                                         context.exposure_att[var2])
        rolled = context.exposure_att[var1]

        # print "var_out]", context.exposure_att[var_out].shape
        # Roll var1 back
        context.exposure_att[var1] = scipy.rollaxis(rolled,
                                                    rolled.ndim - 1, 0)
        # Roll the output so the asset dimension is 0.
        result = context.exposure_att[var_out]
        context.exposure_att[var_out] = scipy.rollaxis(result,
                                                       rolled.ndim - 1, 0)
        # print "var1 unrolled", context.exposure_att[var1].shape
        # print "var2", context.exposure_att[var2].shape
        # print "var_out]", context.exposure_att[var_out].shape


class LoadCsvExposure(Job):

    """
    Read a csv exposure file into the context object.
    """

    def __init__(self):
        super(LoadCsvExposure, self).__init__()
        self.call_funct = LOADCSVEXPOSURE

    def __call__(
            self,
            context,
            file_name,
            exposure_latitude=None,
            exposure_longitude=None,
            use_parallel=True):
        """
        Read a csv exposure file into the context object.

        :param context: The context instance, used to move data around.
        :param file_name: The csv file to load.
        :param exposure_latitude: the title string of the latitude column.
        :param exposure_longitude: the title string of the longitude column.

        Content return:
            exposure_att: Add the file values into this dictionary.
            key: column titles
            value: column values, except the title
        """
        dt = misc.get_file_mtime(file_name)
        expent = context.prov.entity(":Exposure data", 
                            {'dcterms:title': 'Exposure data',
                             'prov:type': 'void:Dataset',
                             'prov:generatedAtTime':dt,
                             'prov:atLocation':os.path.basename(file_name)})
        context.prov.used(context.provlabel, expent)
        data_frame = parallel.csv2dict(file_name, use_parallel=use_parallel)
        # FIXME Need to do better error handling
        # FIXME this function can only be called once.
        # Multiple calls will corrupt the context data.

        if exposure_latitude is None:
            lat_key = EX_LAT
        else:
            lat_key = exposure_latitude

        try:
            context.exposure_lat = data_frame[lat_key].values
            del data_frame[lat_key]
        except KeyError:
            msg = "No Exposure latitude column labelled '%s'." % lat_key
            raise RuntimeError(msg)

        if exposure_longitude is None:
            long_key = EX_LONG
        else:
            long_key = exposure_longitude

        try:
            context.exposure_long = data_frame[long_key].values
            del data_frame[long_key]
        except KeyError:
            msg = "No Exposure longitude column labelled '%s'." % long_key
            raise RuntimeError(msg)

        context.exposure_att = data_frame
        #for key in data_frame:
        #    context.exposure_att[key] = data_frame[key].values


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
            dt = misc.get_file_mtime(file_name)
            vulent = context.prov.entity(":vulnerability file",
                                         {'prov:type': 'prov:Collection',
                                          'prov:generatedAtTime':dt,
                                          'prov:atLocation':os.path.basename(file_name)})
            context.prov.used(context.provlabel, vulent)


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
        for k, v in vul_functions_in_exposure.items():
            k1 = context.prov.entity(":vulnerability set",
                                     {"dcterms:title":k,
                                      "prov:value":v})
            context.prov.wasDerivedFrom(context.provlabel, k1)
            context.prov.specializationOf(k1, ":vulnerability file")
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

class PermutateExposure(Job):
    """
    Iterate through the exposure attributes, randomly permutating
    fields each time.
    """

    def __init__(self):
        super(PermutateExposure, self).__init__()
        self.call_funct = PERMUTATE_EXPOSURE

    def __call__(self, context, groupby=None, iterations=1000):
        """
        Calculates the loss for the given vulnerability set, randomly 
        permutating the exposure attributes to arrive at a 
        distribution of loss outcomes.

        :param context: The context instance, used to move data around.
        :param groupby: The name of the exposure attribute to group 
                        exposure assets by before randomly permutating
                        the corresponding vulnerability curves.
        :param iterations: Number of iterations to perform
        
        Content return:
           exposure_vuln_curves: A :class:`pandas.DataFrame` of realised
               vulnerability curves, associated with the exposure
               data.
                key - intensity measure
                value - realised vulnerability curve instance per asset
        """
        vulnerability_set_id = list(context.exposure_vuln_curves)[0]
        field = context.vul_function_titles[vulnerability_set_id]

        losses = np.zeros((iterations, len(context.exposure_att)))
        for n in range(iterations):
            context.exposure_att = \
                misc.permutate_att_values(context.exposure_att, 
                                          field, groupby=groupby)

            for intensity_key in context.exposure_vuln_curves:
                SelectVulnFunction().__call__(context, variability_method={
                                                    intensity_key: 'mean'})
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

                losses[n, :] = vuln_curve.look_up(intensities)
                # By adding in a new attribute for each iteration, we can 
                # capture all the possible permutations of loss outcomes. 
                # This leads to a rather substantial output data volume, 
                # especially when considering the larger exposure datasets
                # that will be used in real applications, and the number of 
                # iterations that should be used to achieve convergence.
                loss_iteration = loss_category_type + "_{0:06d}".format(n)
                field_iteration = field + "_{0:06d}".format(n)
                context.exposure_att[loss_iteration] = losses[n, :]
                context.exposure_att[field_iteration] = context.exposure_att[field]
            mean_loss = np.mean(losses, axis=0)
            loss_sd = np.std(losses, axis=0)

            loss_category_type_sd = loss_category_type + "_sd"
            context.exposure_att[loss_category_type] = mean_loss
            context.exposure_att[loss_category_type_sd] = loss_sd

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
                 file_list=None, file_format=None, variable=None,
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
            a_raster = raster_module.Raster.from_array(
                raster, upper_left_x,
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
            file_data = np.where(file_data == no_data_value, np.NAN,
                                 file_data)
            context.exposure_att[attribute_label] = file_data
        else:
            if isinstance(file_list, str):
                file_list = [file_list]

            for f in file_list:                    
                dt = misc.get_file_mtime(f)
                atts = {"dcterms:title":"Source hazard data",
                        "prov:type":"prov:Dataset",
                        "prov:atLocation":os.path.basename(f),
                        "prov:format":os.path.splitext(f)[1].replace('.',''),
                        "prov:generatedAtTime":dt,}
                if file_format == 'nc' and variable:
                    atts['prov:variable'] = variable
                hazent = context.prov.entity(":Hazard data", atts)
                context.prov.used(context.provlabel, hazent)

            if file_format == 'nc' and variable:
                file_list = misc.mod_file_list(file_list, variable)

            file_data, extent = raster_module.files_raster_data_at_points(
                context.exposure_long,
                context.exposure_lat, file_list)
            file_data = np.where(file_data == no_data_value, np.NAN,
                                 file_data)
            context.exposure_att[attribute_label] = file_data

            if clip_exposure2all_hazards:
                # Clipping the exposure points after the data has been added.
                # Not optimised for speed, but easy to implement.
                context.clip_exposure(*extent)

class AggregateLoss(Job):
    """
    Aggregate loss attributes based on the ``groupby`` attribute 
    used in the permutation of the vulnerability curves.
    """
    def __init__(self):
        super(AggregateLoss, self).__init__()
        self.call_funct = AGGREGATE_LOSS

    def __call__(self, context, groupby=None, kwargs=None):
        """
        Aggregate using `pandas.GroupBy` objects
        
        :param context: The context instance, used to move data around.
        :param groupby: The name of the exposure attribute to group 
                        exposure assets by before performing aggregations 
                        (sum, mean, etc.).
        """
        context.aggregate_loss(groupby, kwargs)

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

class SaveAggregation(Job):

    def __init__(self):
        super(SaveAggregation, self).__init__()
        self.call_funct = SAVEAGG

    def __call__(self, context, file_name=None,  use_parallel=True):
        """
        Save all of the aggregated exposure information in the context.

        :param context: The context instance, used to move data around.
        :params file_name: The file where the expsoure data will go.
        """
        context.save_exposure_aggregation(file_name,
                                          use_parallel=use_parallel)

class Aggregate(Job):

    def __init__(self):
        super(Aggregate, self).__init__()
        self.call_funct = AGGREGATE

    def __call__(self, context, file_name=None, boundaries=None,
                 impactcode=None, boundarycode=None, use_parallel=True):
        context.save_aggregation(file_name,
                                 boundaries,
                                 impactcode,
                                 boundarycode,
                                 use_parallel=use_parallel)

class SaveProvenance(Job):

    def __init__(self):
        super(SaveProvenance, self).__init__()
        self.call_funct = SAVEPROVENANCE
    
    def __call__(self, context, file_name=None):
        """
        Save provenance information. 

        By default we save to xml format.
        """

        dot = prov_to_dot(context.prov)
        dot.write_png(file_name.replace('.xml', '.png'))
        context.prov.serialize(file_name, format='xml')
# ____________________________________________________
# ----------------------------------------------------
#                KEEP THIS AT THE END
# ____________________________________________________

JOBS = misc.instanciate_classes(sys.modules[__name__])

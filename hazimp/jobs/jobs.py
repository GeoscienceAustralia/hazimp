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
import sys
from typing import Union
import datetime
import scipy
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
TABULATE = 'tabulate'
CATEGORISE = 'categorise'
SAVEPROVENANCE = 'saveprovenance'
DATEFMT = "%Y-%m-%d %H:%M:%S"


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

        rolled = context.exposure_att[var1]
        context.exposure_att[var1] = scipy.rollaxis(rolled, 0,
                                                    rolled.ndim)

        context.exposure_att[var_out] = (context.exposure_att[var1] *
                                         context.exposure_att[var2])
        rolled = context.exposure_att[var1]

        # Roll var1 back
        context.exposure_att[var1] = scipy.rollaxis(rolled,
                                                    rolled.ndim - 1, 0)

        # Roll the output so the asset dimension is 0.
        result = context.exposure_att[var_out]
        context.exposure_att[var_out] = scipy.rollaxis(result,
                                                       rolled.ndim - 1, 0)


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
        file_name = misc.download_file_from_s3_if_needed(file_name)
        dt = misc.get_file_mtime(file_name)
        expent = context.prov.entity(":Exposure data",
                                     {'dcterms:title': 'Exposure data',
                                      'prov:type': 'prov:Dataset',
                                      'prov:format': 'Comma-separated values',
                                      'prov:generatedAtTime': dt,
                                      'prov:atLocation':
                                          os.path.basename(file_name)})
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


class LoadXmlVulnerability(Job):

    """
    Read the vulnerability sets into the context object.
    """

    def __init__(self):
        super(LoadXmlVulnerability, self).__init__()
        self.call_funct = LOADXMLVULNERABILITY

    def __call__(self, context, file_name: Union[str, list]):
        """
        Read XML vulnerability files into the context object.

        :param context: The context instance, used to move data around.
        :param file_name: The xml files to load.
        """
        if file_name is not None:
            if isinstance(file_name, str):
                file_name = [file_name]

            vuln_sets = vuln_sets_from_xml_file(file_name)
            context.vulnerability_sets.update(vuln_sets)

            for filename in file_name:
                dt = misc.get_file_mtime(filename)
                vulent = context.prov.entity(":vulnerability file",
                                             {'prov:type': 'prov:Collection',
                                              'prov:generatedAtTime': dt,
                                              'prov:atLocation':
                                                  os.path.basename(filename)})
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
                                     {"dcterms:title": k,
                                      "prov:value": v})
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

    def __call__(self, context, groupby=None, iterations=1000, quantile=0.95):
        """
        Calculates the loss for the given vulnerability set, randomly
        permutating the exposure attributes to arrive at a
        distribution of loss outcomes. We do not take the absolute maximum
        loss, rather we use an upper quantile of the accumulated loss to define
        "maximum" (or "worst-case") loss.

        The result is that the "structural_max" is the loss associated with the
        permutation that gives the upper percentile of total loss for the
        analysis area. The "structural" value is the average loss across all
        permutations.

        :param context: The context instance, used to move data around.
        :param groupby: The name of the exposure attribute to group
                        exposure assets by before randomly permutating
                        the corresponding vulnerability curves.
        :param iterations: Number of iterations to perform
        :param quantile: Represents the "maximum" event loss. Default=0.95

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
        starttime = datetime.datetime.now()
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
                    msg += ('vulnerability_set_id is %s. \n' %
                            vulnerability_set_id)
                    raise RuntimeError(msg)

                losses[n, :] = vuln_curve.look_up(intensities)

        endtime = datetime.datetime.now()
        # Mean loss per unit across all permutations:
        mean_loss = np.mean(losses, axis=0)

        # Mean loss across separate permutations:
        lossmean = losses.mean(axis=1)

        # Gives the index of the permutation with the 95th percentile mean loss
        idx = np.abs(lossmean - np.quantile(lossmean, quantile)).argmin()

        # Unit losses for the event with 95th percentile mean loss
        lossmax = losses[idx, :]
        context.exposure_att[loss_category_type] = mean_loss
        loss_category_type_max = loss_category_type + '_max'
        context.exposure_att[loss_category_type_max] = lossmax
        permatts = {"dcterms:title": "Exposure permutation",
                    ":iterations": iterations,
                    ":GroupingField": groupby,
                    ":quantile": quantile}
        permact = context.prov.activity(":ExposurePermutation",
                                        starttime.strftime(DATEFMT),
                                        endtime.strftime(DATEFMT),
                                        permatts)
        perment = context.prov.entity(":Permuted exposure",
                                      {"prov:label": "Permuted exposure data",
                                       "prov:type": "void:Dataset",
                                       }
                                      )
        context.prov.wasGeneratedBy(perment, permact)
        context.prov.used(permact, ":Exposure data")
        context.prov.used(context.provlabel, perment)


class LoadRaster(Job):

    """
    Load one or more files and get the value for all the
    points. Primarily this will be used to load hazard data.

    There may be NAN values in this data
    """

    def __init__(self):
        super(LoadRaster, self).__init__()
        self.call_funct = LOADRASTER

    def __call__(self, context, attribute_label, file_list,
                 clip_exposure2all_hazards=False,
                 file_format=None, variable=None, no_data_value=None):
        """
        Load one or more files and get the value for all the
        exposure points. All files have to be of the same attribute.
        Alternatively a numeric array of the raster data can be passed in.

        :param context: The context instance, used to move data around.
        :param attribute_label: The string to be associated with this data.
        :param clip_exposure2all_hazards: True if the exposure data is
            clippped to the hazard data, so no hazard values are ignored.
        :param file_list: A list of files or a single file to be loaded.
        :param no_data_value: Values in the raster that represent no data.

        Context return:
           exposure_att: Add the file values into this dictionary.
               key: column titles
               value: column values, except the title
        """

        if isinstance(file_list, str):
            file_list = [file_list]

        for f in file_list:
            f = misc.download_file_from_s3_if_needed(f)
            dt = misc.get_file_mtime(f)
            current_file_format = os.path.splitext(f)[1].replace('.', '')
            atts = {"dcterms:title": "Source hazard data",
                    "prov:type": "prov:Dataset",
                    "prov:atLocation": os.path.basename(f),
                    "prov:format": current_file_format,
                    "prov:generatedAtTime": dt, }
            if current_file_format == 'nc' and variable:
                atts['prov:variable'] = variable
            hazent = context.prov.entity(":Hazard data", atts)
            context.prov.used(context.provlabel, hazent)

        if file_format == 'nc' and variable:
            file_list = misc.mod_file_list(file_list, variable)

        file_data, extent = raster_module.files_raster_data_at_points(
            context.exposure_long,
            context.exposure_lat, file_list)
        file_data[file_data == no_data_value] = np.NAN

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

    def __call__(self, context, file_name=None, use_parallel=True):
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

    def __call__(self, context, filename=None, boundaries=None,
                 impactcode=None, boundarycode=None, categories=True,
                 fields=None, categorise=None, use_parallel=True):
        # Default filename to use when no output filename is specified
        if filename is None:
            filename = ['output.json']

        # Ensure filename is a list - maintains backwards compatibility with
        # earlier versions that only supported a single output filename/type
        if isinstance(filename, str):
            filename = [filename]

        # Defaults fields to use when none are provided to maintain
        # backwards compatibility
        if fields is None:
            fields = {'structural': ['mean']}

        for file in filename:
            context.save_aggregation(file,
                                     boundaries,
                                     impactcode,
                                     boundarycode,
                                     categories,
                                     fields,
                                     categorise,
                                     use_parallel=use_parallel)


class Tabulate(Job):

    def __init__(self):
        super(Tabulate, self).__init__()
        self.call_funct = TABULATE

    def __call__(self, context, file_name=None, index=None,
                 columns=None, aggfunc=None, use_parallel=True):
        context.tabulate(file_name, index, columns, aggfunc)


class Categorise(Job):

    def __init__(self):
        super(Categorise, self).__init__()
        self.call_funct = CATEGORISE

    def __call__(self, context, bins=None, labels=None, field_name=None):
        context.categorise(bins, labels, field_name)


class SaveProvenance(Job):

    def __init__(self):
        super(SaveProvenance, self).__init__()
        self.call_funct = SAVEPROVENANCE

    def __call__(self, context, file_name=None):
        """
        Save provenance information.

        By default we save to xml format.
        """

        [file_name, bucket_name, bucket_key] = \
            misc.create_temp_file_path_for_s3(file_name)
        [basename, ext] = os.path.splitext(file_name)
        endtime = datetime.datetime.now().strftime(DATEFMT)
        context.prov.activity(context.provlabel,
                              context.provstarttime,
                              endtime,
                              {"dcterms:title": context.provtitle,
                               "prov:type": "void:Analysis"}
                              )
        context.prov.wasAttributedTo(context.provlabel, ":hazimp")
        dot = prov_to_dot(context.prov)
        dot.write_png(basename + '.png')
        context.prov.serialize(file_name, format='xml')
        if bucket_key is not None:
            misc.upload_to_s3_if_applicable(file_name,
                                            bucket_name,
                                            bucket_key)
            misc.upload_to_s3_if_applicable(basename + '.png',
                                            bucket_name,
                                            bucket_key[:-len(ext)] + '.png')
# ____________________________________________________
# ----------------------------------------------------
#                KEEP THIS AT THE END
# ____________________________________________________


JOBS = misc.instanciate_classes(sys.modules[__name__])

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

# W0221: 65:ConfigAwarePipeLine.run: Arguments number differs from
# overridden method
# pylint: disable=W0221,R0205,R0902
# I'm ok with .run having more arg's
# I should use the ABC though.

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

import os
import getpass
from datetime import datetime
import logging
import csv

import numpy
import pandas as pd

from prov.model import ProvDocument

from hazimp import misc
from hazimp import parallel
from hazimp import aggregate

LOGGER = logging.getLogger(__name__)
DATEFMT = "%Y-%m-%d %H:%M:%S %Z"

# The standard string names in the context instance
EX_LAT = 'exposure_latitude'
EX_LONG = 'exposure_longitude'

# WARNING
# There is high coupling between this and the jobs/vulnerability
# curve module.  This holds the data, the methods are spread out.
# Consider refactoring by generalising the data this class holds
# and accessing the data via methods.


class Context(object):

    """
    Context is a singleton storing all of the run specific data, such as the
    exposure features and their attributes, vulnerability sets, aggregations,
    pivot tables, etc.
    """

    def __init__(self):
        # Warning;
        # If new data is added with a site dimension the
        # clip exposure function may need to be updated
        # so the site data stays consistent.

        # --------------  These variables are saved ----
        #  If new variables are added the save functions
        # will need to be modified.

        # Latitude and longitude values of the exposure data
        # Has a site dimension
        self.exposure_lat = None
        self.exposure_long = None

        # Data with a site dimension
        # key - data name
        # value - A numpy array. First dimension is site. (0 axis)
        # Has a site dimension
        self.exposure_att = None

        # Data for aggregation across sites
        self.exposure_agg = None

        #
        # --------------  The above variables are saved ----

        # key - intensity measure
        # value - One instance of RealisedVulnerabilityCurves.  An att in this
        #         class has a site dimension.
        self.exposure_vuln_curves = None

        # A dictionary of the vulnerability sets.
        # Not associated with exposures.
        # key - vulnerability set ID
        # value - vulnerability set instance
        self.vulnerability_sets = {}

        # A dictionary with keys being vulnerability_set_ids and
        # value being the exposure attribute who's values are vulnerability
        # function ID's.
        self.vul_function_titles = {}

        # Instantiate the `pivot` attribute to None initially
        self.pivot = None

        # A `prov.ProvDocument` to manage provenance information, including
        # adding required namespaces (TODO: are these all required?)
        self.prov = ProvDocument()
        self.prov.set_default_namespace("")
        self.prov.add_namespace('prov', 'http://www.w3.org/ns/prov#')
        self.prov.add_namespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
        self.prov.add_namespace('foaf', 'http://xmlns.com/foaf/0.1/')
        self.prov.add_namespace('void', 'http://vocab.deri.ie/void#')
        self.prov.add_namespace('dcterms', 'http://purl.org/dc/terms/')

        commit, branch, dt = misc.get_git_commit()
        # Create the fundamental software agent that is this code:
        self.prov.agent(":hazimp",
                        {"prov:type": "prov:SoftwareAgent",
                         "prov:Revision": commit,
                         "prov:branch": branch,
                         "prov:date": dt})

        # Not sure this needs to be the user?
        self.prov.agent(f":{getpass.getuser()}",
                        {"prov:type": "foaf:Person"})
        self.prov.actedOnBehalfOf(":hazimp", f":{getpass.getuser()}")
        self.provlabel = ''
        self.provtitle = ''
        self.provstarttime = datetime.now().strftime(DATEFMT)

    def set_prov_label(self, label, title="HazImp analysis"):
        """
        Set the qualified label for the provenance data

        :param label: the qualified label name
        :param title: Optional value for the dcterms:title element
        """

        self.provlabel = f":{label}"
        self.provtitle = title

    def get_site_shape(self):
        """
        Get the numpy shape of sites the context is storing.
        It is based on the shape of exposure_long.

        :return: The numpy shape of sites the context is storing.
        """
        if self.exposure_long is None:
            shape = (0)
        else:
            shape = self.exposure_long.shape
        return shape

    def clip_exposure(self, min_long, min_lat, max_long, max_lat):
        """ min_long, min_lat, max_long, max_lat
        Clip the exposure data so only the exposure values within
        the rectangle formed by  max_lat, min_lat, max_long and
        min_long are included.

        Note: This must be called before the exposure_vuln_curves
        are determined, since the curves have a site dimension.
        """
        assert self.exposure_vuln_curves is None

        bad_indexes = set()
        bad_indexes = bad_indexes.union(numpy.where(
            self.exposure_long < min_long)[0])
        bad_indexes = bad_indexes.union(numpy.where(
            self.exposure_long > max_long)[0])
        bad_indexes = bad_indexes.union(numpy.where(
            self.exposure_lat < min_lat)[0])
        bad_indexes = bad_indexes.union(numpy.where(
            self.exposure_lat > max_lat)[0])
        good_indexes = numpy.array(list(set(
            range(self.exposure_lat.size)).difference(bad_indexes)), dtype=int)

        if good_indexes.shape[0] == 0:
            self.exposure_lat = numpy.array([])
            self.exposure_long = numpy.array([])
        else:
            self.exposure_lat = self.exposure_lat[good_indexes]
            self.exposure_long = self.exposure_long[good_indexes]

        if isinstance(self.exposure_att, dict):
            for key in self.exposure_att:
                if good_indexes.shape[0] == 0:
                    exp_att = numpy.array([])
                else:
                    exp_att = self.exposure_att[key][good_indexes]
                self.exposure_att[key] = exp_att
        else:
            self.exposure_att = self.exposure_att.take(good_indexes)

    def save_exposure_atts(self, filename, use_parallel=True):
        """
        Save the exposure attributes, including latitude and longitude.
        The file type saved is based on the filename extension.
        Options
           '.npz': Save the arrays into a single file in uncompressed .npz
                   format.

        :param use_parallel: Set to True for parallel behaviour
        Which is only node 0 writing to file.
        :param filename: The file to be written.
        :return write_dict: The whole dictionary, returned for testing.
        """
        [filename, bucket_name, bucket_key] = \
            misc.create_temp_file_path_for_s3(filename)
        s1 = self.prov.entity(":HazImp output file",
                              {"prov:label": "Full HazImp output file",
                               "prov:type": "void:Dataset",
                               "prov:atLocation": os.path.basename(filename)})
        a1 = self.prov.activity(":SaveImpactData",
                                datetime.now().strftime(DATEFMT),
                                None)
        self.prov.wasGeneratedBy(s1, a1)
        self.prov.wasInformedBy(a1, self.provlabel)
        write_dict = self.exposure_att.copy()
        write_dict[EX_LAT] = self.exposure_lat
        write_dict[EX_LONG] = self.exposure_long

        if use_parallel:
            assert misc.INTID in write_dict
            write_dict = parallel.gather_dict(write_dict,
                                              write_dict[misc.INTID])

        if parallel.STATE.rank == 0 or not use_parallel:
            if filename[-4:] == '.csv':
                save_csv(write_dict, filename)
            else:
                numpy.savez(filename, **write_dict)
            misc.upload_to_s3_if_applicable(filename, bucket_name, bucket_key)
            # The write_dict is returned for testing
            # When running in paralled this is a way of getting all
            # of the context info
            return write_dict

    def save_exposure_aggregation(self, filename, use_parallel=True):
        """
        Save the aggregated exposure attributes.
        The file type saved is based on the filename extension.
        Options
           '.npz': Save the arrays into a single file in uncompressed .npz
                   format.

        :param use_parallel: Set to True for parallel behaviour which
        is only node 0 writing to file.
        :param filename: The file to be written.
        :return write_dict: The whole dictionary, returned for testing.
        """
        write_dict = self.exposure_agg.copy()

        s1 = self.prov.entity(":Aggregated HazImp output file",
                              {"prov:label": "Aggregated HazImp output file",
                               "prov:type": "void:Dataset",
                               "prov:atLocation": os.path.basename(filename)})
        a1 = self.prov.activity(":SaveAggregatedImpactData",
                                datetime.now().strftime(DATEFMT),
                                None)
        self.prov.wasGeneratedBy(s1, a1)
        self.prov.wasInformedBy(a1, self.prov.activity(":AggregateLoss"))

        if parallel.STATE.rank == 0 or not use_parallel:
            if filename[-4:] == '.csv':
                save_csv_agg(write_dict, filename)
            else:
                numpy.savez(filename, **write_dict)
            # The write_dict is returned for testing
            # When running in paralled this is a way of getting all
            # of the context info
            return write_dict

    def save_aggregation(self, filename, boundaries, impactcode,
                         boundarycode, categories, fields, categorise,
                         use_parallel=True):
        """
        Save data aggregated to geospatial regions

        :param str filename: Destination filename
        :param bool use_parallel: True for parallel behaviout, which
                                  is only node 0 writing to file

        """
        LOGGER.info("Saving aggregated data")
        boundaries = misc.download_file_from_s3_if_needed(boundaries)
        [filename, bucket_name, bucket_key] = \
            misc.create_temp_file_path_for_s3(filename)
        write_dict = self.exposure_att.copy()
        dt = datetime.now().strftime(DATEFMT)
        atts = {"prov:type": "void:Dataset",
                "prov:atLocation": os.path.basename(boundaries),
                "prov:generatedAtTime": misc.get_file_mtime(boundaries),
                "void:boundary_code": boundarycode}

        bdyent = self.prov.entity(":Aggregation boundaries", atts)
        aggact = self.prov.activity(":AggregationByRegions", dt, None,
                                    {'prov:type': "Spatial aggregation",
                                     'void:functions': repr(fields)})
        aggatts = {"prov:type": "void:Dataset",
                   "prov:atLocation": os.path.basename(filename),
                   "prov:generatedAtTime": dt}
        aggfileent = self.prov.entity(":AggregationFile", aggatts)
        self.prov.used(aggact, bdyent)
        self.prov.wasInformedBy(aggact, self.provlabel)
        self.prov.wasGeneratedBy(aggfileent, aggact)
        if parallel.STATE.rank == 0 or not use_parallel:
            aggregate.choropleth(write_dict, boundaries, impactcode,
                                 boundarycode, filename, fields, categories,
                                 categorise)
            misc.upload_to_s3_if_applicable(filename, bucket_name, bucket_key)
            if (bucket_name is not None and
                    bucket_key is not None and
                    bucket_key.endswith('.shp')):
                [rootname, ext] = os.path.splitext(filename)
                base_bucket_key = bucket_key[:-len(ext)]
                misc.upload_to_s3_if_applicable(rootname + '.dbf',
                                                bucket_name,
                                                base_bucket_key + '.dbf')
                misc.upload_to_s3_if_applicable(rootname + '.shx',
                                                bucket_name,
                                                base_bucket_key + '.shx')
                misc.upload_to_s3_if_applicable(rootname + '.prj',
                                                bucket_name,
                                                base_bucket_key + '.prj')
                misc.upload_to_s3_if_applicable(rootname + '.cpg',
                                                bucket_name,
                                                base_bucket_key + '.cpg', True)

    def aggregate_loss(self, groupby=None, kwargs=None):
        """
        Aggregate data by the `groupby` attribute, using the `kwargs` to
        perform any arithmetic aggregation on fields (e.g. summation,
        mean, etc.)

        :param str groupby: A column in the `DataFrame` that corresponds to
        regions by which to aggregate data
        :param dict kwargs: A `dict` with keys of valid column names (from the
        `DataFrame`) and values being lists of aggregation functions to apply
        to the columns.

        For example::

        kwargs = {'REPLACEMENT_VALUE': ['mean', 'sum'],
                'structural': ['mean', 'std']}


        See
        https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#aggregation
        for more guidance on using aggregation with `DataFrames`

        """
        LOGGER.info(f"Aggregating loss using {groupby} attribute")
        a1 = self.prov.activity(":AggregateLoss",
                                datetime.now().strftime(DATEFMT),
                                None,
                                {"prov:type": "Aggregation",
                                 "void:aggregator": repr(groupby)})
        self.prov.wasInformedBy(a1, self.provlabel)
        self.exposure_agg = aggregate.aggregate_loss_atts(self.exposure_att,
                                                          groupby, kwargs)

    def categorise(self, bins, labels, field_name):
        """
        Bin values into discrete intervals.

        :param list bins: Monotonically increasing array of bin edges,
                          including the rightmost edge, allowing for
                          non-uniform bin widths.
        :param labels: Specifies the labels for the returned
                       bins. Must be the same length as the resulting bins.
        :param str field_name: Name of the new column in the `exposure_att`
                                `DataFrame`
        """

        for intensity_key in self.exposure_vuln_curves:
            vc = self.exposure_vuln_curves[intensity_key]
            lct = vc.loss_category_type
        LOGGER.info(f"Categorising {lct} values into {len(labels)} categories")
        self.exposure_att[field_name] = pd.cut(self.exposure_att[lct],
                                               bins, right=False,
                                               labels=labels)

    def tabulate(self, file_name, index=None, columns=None, aggfunc=None):
        """
        Reshape data (produce a "pivot" table) based on column values. Uses
        unique values from specified `index` / `columns` to form axes of the
        resulting DataFrame, then writes to an Excel file. This function does
        not support data aggregation - multiple values will result in a
        MultiIndex in the columns.
        See
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html
        for further details.

        Parameters
        ----------
        file_name : destination for the pivot table
        index : column or list of columns
            Keys to group by on the pivot table index.  If an array is passed,
            it is being used as the same manner as column values.
        columns : column, or list of the columns
            Keys to group by on the pivot table column.  If an array is passed,
            it is being used as the same manner as column values.
        aggfunc : function, list of functions, dict, default numpy.mean
            If list of functions passed, the resulting pivot table will have
            hierarchical columns whose top level are the function names
            (inferred from the function objects themselves)
            If dict is passed, the key is column to aggregate and value
            is function or list of functions.

        Example:

        Include the following in the configuration file:
         - tabulate:
            file_name: wind_impact_table.xlsx
            index: MESHBLOCK_CODE_2011
            columns: Damage state
            aggfunc: size

        This will produce a file called "wind_impact_table.xlsx", with the
        count of buildings in each "Damage state", grouped by the `index` field
        `MESHBLOCK_CODE_2011`
        """
        if index not in self.exposure_att.columns:
            LOGGER.error(f"Cannot tabulate data using {index} as index")
            LOGGER.error(f"{index} is not an attribute of the exposure data")
            return

        if columns not in self.exposure_att.columns:
            LOGGER.error(
                f"Required attribute(s) {columns} not in the exposure data")
            LOGGER.error(
                "Maybe you need to run a categorise job before this one?")
            return

        dt = datetime.now().strftime(DATEFMT)
        a1 = self.prov.activity(":Tabulate", dt, None,
                                {"prov:type": "Tabulation",
                                 "void:aggregator": repr(index),
                                 "void:attributes": repr(columns),
                                 "void:aggregation": repr(aggfunc)})
        tblatts = {"prov:type": "void:Dataset",
                   "prov:atLocation": os.path.basename(file_name),
                   "prov:generatedAtTime": dt}
        tblfileent = self.prov.entity(":TabulationFile", tblatts)

        self.pivot = self.exposure_att.pivot_table(index=index,
                                                   columns=columns,
                                                   aggfunc=aggfunc,
                                                   fill_value=0)

        # Add a row that sums the columns, then another to record the
        # percentage in each column:
        self.pivot.loc['Total', :] = self.pivot.sum(axis=0).values
        self.pivot.loc['Percent', :] = 100. * self.pivot.loc['Total'].values\
            / self.pivot.loc['Total'].sum()
        try:
            self.pivot.to_excel(file_name)
        except TypeError as te:
            LOGGER.error(te)
            raise
        except KeyError as ke:
            LOGGER.error(ke)
            raise
        except ValueError as ve:
            LOGGER.error(f"Unable to save tabulated data to {file_name}")
            LOGGER.error(ve)
        else:
            self.prov.wasGeneratedBy(tblfileent, a1)
            self.prov.wasInformedBy(a1, self.provlabel)


def save_csv(write_dict, filename):
    """
    Save a dictionary of arrays as a csv file.
    the first dimension in the arrays is assumed to have the save length
    for all arrays.
    In the csv file the keys become titles and the arrays become values.

    If the array is higher than 1d the other dimensions are averaged to get a
    1d array.

    :param  write_dict: Write as a csv file.
    :type write_dict: Dictionary.
    :param filename: The csv file will be written here.
    """
    keys = list(write_dict.keys())
    header = list(keys)

    #  Lat, long ordering for the header
    header.remove(EX_LAT)
    header.remove(EX_LONG)
    header.insert(0, EX_LAT)
    header.insert(1, EX_LONG)
    body = None
    for key in header:
        #  Only one dimension can be saved.
        #  Average the results to the Site (first) dimension.
        only_1d = misc.squash_narray(write_dict[key])
        if body is None:
            body = only_1d
        else:
            # NUMPY1.6 loses significant figures
            body = numpy.column_stack((body, only_1d))
    # Need numpy 1.7 > to do headers
    # numpy.savetxt(filename, body, delimiter=',', header='yeah')

    dirname = os.path.dirname(filename)
    if dirname and not os.path.isdir(dirname):
        LOGGER.warning(f"{dirname} does not exist - trying to create it")
        os.makedirs(dirname)

    hnd = open(filename, 'w', newline='')

    writer = csv.writer(hnd, delimiter=',')
    writer.writerow(header)
    for i in range(body.shape[0]):
        writer.writerow(list(body[i, :]))


def save_csv_agg(write_dict, filename):
    """
    Save a `pandas.DataFrame` as a csv file.
    the first dimension in the arrays is assumed to have the save length
    for all arrays.
    In the csv file the keys become titles and the arrays become values.

    If the array is higher than 1d the other dimensions are averaged to get a
    1d array.

    :param  write_dict: Write as a csv file.
    :type write_dict: Dictionary.
    :param filename: The csv file will be written here.
    """

    dirname = os.path.dirname(filename)
    if dirname and not os.path.isdir(dirname):
        LOGGER.warning(f"{dirname} does not exist - trying to create it")
        os.makedirs(dirname)

    write_dict.to_csv(filename, index_label='FID')

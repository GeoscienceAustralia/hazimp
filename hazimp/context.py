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
# pylint: disable=W0221
# I'm ok with .run having more arg's
# I should use the ABC though.

"""
The purpose of this module is to provide objects
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

import os
import sys
import numpy
import csv
import geopandas as gpd

from prov.model import ProvDocument

from hazimp import misc
from hazimp import parallel

import logging

from datetime import datetime

LOGGER=logging.getLogger(__name__)

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
    Context is a singlton storing all
    of the run specific data.
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

        # A `prov.ProvDocument` to manage provenance information, including
        # adding required namespaces
        self.prov = ProvDocument()
        self.prov.add_namespace('prov', 'http://www.w3.org/ns/prov#')
        self.prov.add_namespace('xsd',  'http://www.w3.org/2001/XMLSchema#')
        self.prov.add_namespace('foaf', 'http://xmlns.com/foaf/0.1/')
        self.prov.add_namespace('void', 'http://vocab.deri.ie/void#')
        self.prov.add_namespace('dcterms', 'http://purl.org/dc/terms/')
        self.provlabel = ''

    def set_prov_label(self, label, title="HazImp analysis"):
        """
        Set the qualified label for the provenance data
        """

        self.provlabel = f"prov:{label}"
        self.prov.activity(f"prov:{label}", datetime.now(), None,
                           {f"dcterms:title":title,
                           f"prov:type":"void:Analysis"})

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

        if good_indexes.shape[0] is 0:
            self.exposure_lat = numpy.array([])
            self.exposure_long = numpy.array([])
        else:
            self.exposure_lat = self.exposure_lat[good_indexes]
            self.exposure_long = self.exposure_long[good_indexes]

        
        if isinstance(self.exposure_att, dict):
            for key in self.exposure_att:
                if good_indexes.shape[0] is 0:
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
        s1 = self.prov.entity(f"prov:{os.path.basename(filename)}",
                              {f"prov:label":"Full HazImp output file",
                              f"prov:type":"void:Dataset"})
        a1 = self.prov.activity("prov:SaveImpactData", datetime.now(), None)
        self.prov.wasGeneratedBy(s1, a1)
        self.prov.wasGeneratedBy(self.provlabel, s1)
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

        #if use_parallel:
            #assert misc.INTID in write_dict
        #    write_dict = parallel.gather_dict(write_dict,
        #                                      write_dict[misc.INTID])

        if parallel.STATE.rank == 0 or not use_parallel:
            if filename[-4:] == '.csv':
                save_csv_agg(write_dict, filename)
            else:
                numpy.savez(filename, **write_dict)
            # The write_dict is returned for testing
            # When running in paralled this is a way of getting all
            # of the context info
            return write_dict

    def save_aggregation(self, filename, boundaries, impactcode, boundarycode, use_parallel=True):
        """
        Save data aggregated to geospatial regions
        
        :param str filename: Destination filename
        :param bool use_parallel: True for parallel behaviout, which 
                                  is only node 0 writing to file

        """
        LOGGER.info("Saving aggregated data")
        write_dict = self.exposure_att.copy()
        aggent = self.prov.entity(f"prov:{os.path.basename(boundaries)}", 
                                 {"prov:label":"Aggregation boundaries",
                                  "prov:type":"void:Dataset",
                                  "void:path": boundaries,
                                  "void:boundary_code":boundarycode})
        aggact = self.prov.activity("prov:AggregationByRegions", datetime.now(), None, 
                                    {'prov:type':"Spatial aggregation"})
        self.prov.used(aggact, aggent)
        self.prov.used(self.provlabel, aggent)
        if parallel.STATE.rank == 0 or not use_parallel:
            misc.choropleth(write_dict, boundaries, impactcode, boundarycode, filename)
        else:
            pass

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
    if not os.path.isdir(dirname):
        LOGGER.warn(f"{dirname} does not exist - trying to create it")
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
    if dirname == '':
        pass
    elif not os.path.isdir(dirname):
        LOGGER.warn(f"{dirname} does not exist - trying to create it")
        os.makedirs(dirname)
        
    try:
        write_dict.to_csv(filename, index_label='FID')
    except FileNotFoundError:
        LOGGER.error(f"Cannot write to {filename}")
        sys.exit(1)
    """
    keys = write_dict.keys()
    header = list(keys)

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
    hnd = open(filename, 'wb')
    writer = csv.writer(hnd, delimiter=',')
    writer.writerow(header)
    for i in range(body.shape[0]):
        writer.writerow(list(body[i, :]))
    """
    


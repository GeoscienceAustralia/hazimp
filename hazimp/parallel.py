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

"""
Functions that haven't found a proper module.

"""
import atexit

import socket
import numpy

from hazimp import misc


class Parallel(object):

    """ Parallelise to run on a cluster.

    :param rank: What is the id of this node in the cluster.
    :param size: How many processors are there in the cluster.
    :param node: name of the cluster node.
    :param is_parallel: True if parallel is operational
    :param file_tag: A string that can be added to files to identify who
      wrote the file.

    """

    def __init__(self):
        """
        Use is_parallel = False to stop parallelism, eg when running
        several scenarios.

        """

        try:
            import pypar   # pylint: disable=W0404
        except ImportError:
            self._not_parallel()
        else:
            if pypar.size() >= 2:
                self.rank = pypar.rank()
                self.size = pypar.size()
                self.node = pypar.get_processor_name()
                self.is_parallel = True
                self.file_tag = str(self.rank)
                self.log_file_tag = str(self.rank)

                # Ensure a clean MPI exit
                atexit.register(pypar.finalize)
            else:
                self._not_parallel()

    def _not_parallel(self):
        """
        Set the attributes if there is only one node.

        """
        self.rank = 0
        self.size = 1
        self.node = socket.gethostname()  # The host name
        self.is_parallel = False
        self.log_file_tag = str(self.rank)


STATE = Parallel()


def scatter_dict(whole):
    """
    Broadcast and recieve a dictionary where the values are 1d arrays
    and the arrays are chunked for the workers.
    Only rank 0 needs the whole dictionary.

    :param whole: The dictionary of 1d arrays to subdict.
    :returns: (chunk of dictionary of 1d arrays, indexes of whole array)

    """
    if not STATE.is_parallel:
        array_len = len(whole[list(whole.keys())[0]])
        return whole, numpy.array(list(range(0, array_len)))
    else:
        import pypar     # pylint: disable=W0404

    if STATE.rank == 0:
        array_len = len(whole[list(whole.keys())[0]])
        for pro in range(0, STATE.size):
            temp_indexes = numpy.array(list(range(pro, array_len, STATE.size)))
            temp_subdict = {}
            for key in list(whole.keys()):
                temp_subdict[key] = whole[key][temp_indexes]
            if pro == 0:
                indexes = temp_indexes
                subdict = temp_subdict
            else:
                pypar.send(temp_indexes, pro)
                pypar.send(temp_subdict, pro)
    else:
        indexes = pypar.receive(0)
        subdict = pypar.receive(0)
    return subdict, indexes


def gather_dict(subdict, indexes):
    """
    Recieve a dictionary from the children where the values are 1d arrays
    and the arrays are chunks of the whole dictionary.

    :param indexes: The indexes into the whole array.
    :param subdict: The dictionary of 1d arrays to subset.
    :returns: whole array

    """
    if not STATE.is_parallel:
        return subdict
    else:
        import pypar    # pylint: disable=W0404

    # Note, putting dictionary back sequentially
    if STATE.rank == 0:
        whole = {}
        array_len = indexes[-1]  # highest index in node 0 array
        all_indexes = [[]]  # Empty list for processor 0
        for pro in range(1, STATE.size):
            temp_indexes = pypar.receive(pro)
            all_indexes.append(temp_indexes)
            if temp_indexes[-1] > array_len:
                array_len = temp_indexes[-1]
        # Create the whole dictionary, filled with rank 0 info
        for key in list(subdict.keys()):
            # Work-out the shape of arrays
            array_shape = list(subdict[key].shape)
            array_shape[0] = array_len + 1
            whole[key] = numpy.empty(tuple(array_shape), subdict[key].dtype)
            whole[key][indexes, ...] = subdict[key]
        for pro in range(1, STATE.size):
            subdict = pypar.receive(pro)
            for key in list(whole.keys()):
                whole[key][all_indexes[pro], ...] = subdict[key]
        return whole
    else:
        pypar.send(indexes, 0)
        pypar.send(subdict, 0)


def csv2dict(filename, use_parallel=True):
    """
    Read a csv file in and return the information as a dictionary
    where the key is the column names and the values are column arrays.

    This dictionary will be chunked and sent to all processors.

    :param filename: The csv file path string.
    :returns: subsection of the array

    """
    if STATE.is_parallel and use_parallel:
        whole = None
        if STATE.rank == 0:
            whole = misc.csv2dict(filename, add_ids=True)
        (subdict, _) = scatter_dict(whole)
    else:
        subdict = misc.csv2dict(filename, add_ids=True)
    return subdict

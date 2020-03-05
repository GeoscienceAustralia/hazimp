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
import os
import csv
from collections import defaultdict
import inspect

import numpy
from numpy.random import random_sample, permutation

import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESOURCE_DIR = os.path.join(ROOT_DIR, 'resources')
EXAMPLE_DIR = os.path.join(ROOT_DIR, 'examples')
INTID = 'internal_id'


def csv2dict(filename, add_ids=False):
    """
    Read a csv file in and return the information as a dictionary
    where the key is the column names and the values are column arrays.

    :param add_ids: If True add a key, value of ids, from 0 to n
    :param filename: The csv file path string.
    """
    """
    csvfile = open(filename, 'rb')
    reader = csv.DictReader(csvfile)

    file_dict = defaultdict(list)
    for row in reader:
        for key, val in row.iteritems():
            try:
                val = float(val)
            except (ValueError, TypeError):
                try:
                    val = val.strip()
                    if len(val) == 0:
                        #  This is empty.
                        #  Therefore not a value.
                        val = numpy.nan
                except AttributeError:
                    pass
            file_dict[key.strip()].append(val)

    for key in file_dict.keys():
        file_dict[key] = numpy.asarray(file_dict[key])
    # Get a normal dict now, so KeyErrors are thrown.
    plain_dic = dict(file_dict)
    """
    plain_dic = pd.read_csv(filename, skipinitialspace=True, index_col=False)
    
    if add_ids:
        # Add internal id info
        array_len = len(plain_dic[list(plain_dic.keys())[0]])
        plain_dic[INTID] = numpy.arange(array_len)
    return plain_dic


def instanciate_classes(module):
    """
    Create a dictionary of calc names (key) and the calc instance (value).

    :param module: ??
    """
    callable_instances = {}
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[instance.call_funct] = instance
    return callable_instances


def get_required_args(func):
    """
    Get the arguments required in a function, from the function.

    :param func: The function that you need to know about.
    """

    # http://stackoverflow.com/questions/196960/
    # can-you-list-the-keyword-arguments-a-python-function-receives

    # *args and **kwargs are not required, so ignore them.
    args_and_defaults, _, _, default_vaules = inspect.getargspec(func)
    defaults = []
    if default_vaules is None:
        args = args_and_defaults
    else:
        args = args_and_defaults[:-len(default_vaules)]
        defaults = args_and_defaults[-len(default_vaules):]
    return args, defaults


def squash_narray(ary):
    """
    Reduce an array to 1 dimension. Firstly try to average the values.
    If that doesn't work only take the first dimension.

    :param ary: the numpy array to be squashed.
    :returns: The ary array, averaged to 1d.
    """
    if ary.ndim > 1:
        try:
            d1_ary = ary.reshape((ary.shape[0], -1)).mean(axis=1)
        except TypeError:
            # Can't average, just take the first axis
            d1_ary = ary.reshape((ary.shape[0], -1))[:, 0]
    else:
        d1_ary = ary
    return d1_ary


def add(var, var2):
    """
    Add the values of two numpy arrays together.
    If the values are strings concatenate them.

    :param var: The values in this array are added.
    :param var2: The values in this array are added.
    :returns: The new column name, with the values of Var1 + var2.
    """
    try:
        result = numpy.asarray(var + var2)
    except TypeError:
        # Assume numpy array with strings
        result = numpy.asarray(numpy.core.defchararray.add(var, var2))
    return result


def weighted_values(values, probabilities, size, forced_random=None):
    """
    Return values weighted by the probabilities.

    precondition: The sum of probabilities should sum to 1
    Code from: goo.gl/oBo2zz

    :param values:  The values to go into the final array
    :param probabilities:  The probabilities of the values
    :param size: The array size/shape. Must be 1D.
    :return: The array of values, made using the probabilities
    """

    msg = "Due to numpy.digitize the array must be 1D. "
    assert len(size) == 1, msg

    assert isinstance(probabilities, numpy.ndarray)
    assert isinstance(values, numpy.ndarray)

    assert values.shape == probabilities.shape

    if not numpy.allclose(probabilities.sum(), 1.0, atol=0.01):
        msg = 'Weights should sum to 1.0, got ', probabilities
        raise RuntimeError(msg)

    # Re-normalise weights so they sum to 1 exactly
    probabilities = probabilities / abs(probabilities.sum())  # normalize

    if forced_random is None:
        rand_array = random_sample(size)
    else:
        assert forced_random.shape == size
        rand_array = forced_random
    bins = numpy.add.accumulate(probabilities)
    return values[numpy.digitize(rand_array, bins)]


def sorted_dict_values(adict):
    """
    Given a dictionary return the sorted keys and values,
    sorting with respect to the keys.

    code from: goo.gl/Sb7Czw
    :param adict: A dictionary.
    :return: The sorted keys and the corresponding values
        as two lists.
    """
    keys = sorted(sorted(adict.keys()))
    return keys, [adict[key] for key in keys]

def permutate_att_values(dframe, fields, groupby=None):
    """
    Given a dataframe, return the dataframe with the values in 
    ``fields`` permutated. If the ``groupby`` arg is given,
    then permutate the values of ``fields`` within each grouping of 
    ``groupby``.

    :param dframe: A dataframe. 
    :type dframe: ``pandas.DataFrame``
    :param fields: Name of a field to permutate, or a list of fields.
    :type fields: str or list.
    :param str groupby: Name of the field to group values by.

    :return: The same ``pandas.DataFrame``, with the values of ``fields``
             permutated.

    """
    newdf = dframe.copy()
    if isinstance(fields, str):
        fields = [fields]

    if groupby:
        for field in fields:
            newdf[field] = \
                newdf.groupby(groupby)[field].transform(permutation)
    else:
        for field in fields:
            newdf[field] = newdf[field].transform(permutation)

    return newdf

def aggregate_loss_atts(dframe, groupby=None, kwargs=None):

    grouped = dframe.groupby(groupby, as_index=False)
    
    outdf = grouped.agg(kwargs)
    outdf.columns = ['_'.join(col).strip() for col in outdf.columns.values]
    outdf.reset_index(col_level=1)
    outdf.columns = outdf.columns.get_level_values(0)
    return outdf
        

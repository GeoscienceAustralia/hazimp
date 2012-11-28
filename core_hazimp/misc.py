# -*- coding: utf-8 -*-


"""
Functions that haven't found a proper module.
"""
import csv
from collections import defaultdict
import inspect


def csv2dict(filename):
    """
    Read a csv file in and return the information as a dictionary 
    where the key is the column names and the values are column arrays.
    """
    csvfile = open(filename, 'rb')
    reader = csv.DictReader(csvfile)

    file_dict = defaultdict(list)
    for row in reader:
        for key, val in row.iteritems():
            try:
                val = float(val)
            except ValueError:
                pass
            file_dict[key.strip()].append(val)
    return file_dict

def instanciate_classes(module):
    """
    Create a dictionary of calculation names (key) and the calc instance (value)
    """
    callable_instances = {}
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[instance.call_funct] = instance
    return callable_instances

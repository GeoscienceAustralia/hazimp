# -*- coding: utf-8 -*-


"""
Functins that haven't found a proper module.
"""
import csv
from collections import defaultdict


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
            file_dict[key].append(val)
    return file_dict

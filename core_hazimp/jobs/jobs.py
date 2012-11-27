# -*- coding: utf-8 -*-

from core_hazimp import csv2dict

"""
Jobs are a processing unit that know about the context object.  The
initial jobs will be for setting up the calculations, such as loading
the exposure data.
"""


def load_csv_exposure(context):
    """
    Read a csv exposure file into the context object.
    
    
    Args:
       context: The context instance, used to move data around.
    """
    

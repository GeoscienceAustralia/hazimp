==========
User Guide
==========

Introduction
============

A configuration file is used to define a simulation.  The configuration file is described using yaml, a data serialisation format.  To run HazImp do;::

     python hazimp.py -c wind_v1.yaml

Use -c to specify the configuration file.

HazImp can also be ran in parallel, using mpirun.  For example;::

     mpirun -np 4 python hazimp.py -c wind_v1.yaml
     
To run a wind example do;::

     cd examples/wind
     python ../../core_hazimp/hazimp.py  -c wind_v1.yaml

Templates
=========

The simplest way to use HazImp is with a template. Currently the only
template is for wind hazards.


Wind Template
=============
Given gust information from TCRM and point exposure data the loss associated
with 
each site is calculated using the wind template.
The wind vulnerability functions That are used are built-in to HazImp. They are
defined in the GA internal report 

Here is an example wind configuration file, which uses the wind template.::

     #  python hazimp.py -c wind_v1.yaml
     template: windv1
     load_exposure: 
         file_name: WA_Wind_Exposure_2013_Test_only.csv
         exposure_latitude: LATITUDE
         exposure_longitude: LONGITUDE
     load_wind_ascii: [gust01.txt, gust02.tx]
     save: wind_impact.csv 

The first line is a comment, so this is ignored.
The rest of the file can be understood by the following key value pairs; 

*template*
    The type of template to use.  This example describes the *windv1* template.

*load_exposure*
    This describes how to load the exposure data *load_exposure* has key values pairs of;

    *file_name*
        The name of the file to load.  Currently only csv files are supported.  The first row of the csv file must be the title row.
    
    *exposure_latitude*
        The title of the csv column with latitude values.

    *exposure_longitude*
        The title of the csv column with longitude values.

*load_wind_ascii*
    A list of ascii grid wind hazard files to load or a single file.  The file format is grid ascii.  The values is the file must be *0.2s gust at 10m height m/s*.

*save*
    The file where the results will be saved.  All the results to calculate the damage due to the wind hazard are saved to file. The above example saves to a csv file, since the file name ends in *.csv*.  This has the disadvantage of averaging data from multiple wind hazards.  The information can also be saved as numpy arrays.  This can be done by not using the *.npz* extension.

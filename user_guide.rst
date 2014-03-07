==========
User Guide
==========

Introduction
------------
HazImp is used to simulate the loss of value to structures from natural hazards
using vulnerability curves.  Generally the input information is hazard, such as
a wind speed raster and exposure. The exposure information is currently
supplied as a csv file, with structure locations given in latitude and
longitude. This is combined with vulnerability curve information, described in
an xml file. Figure 1.1 is an example of a vulnerability curve, showing a hazard
value of the x-axis and the loss associated with that hazard on the y-axis;

.. figure:: ./examples/diagrams/example_vuln_curve.png
   :align: center

   *An example vulnerability curve.*



Quick how-to
------------

A configuration file can be used to define a HazImp simulation.  The configuration
file is described using yaml, a data serialisation format.  HazImp can also be
used by another Python application, by passing the configuration infomation in
as a dictionary. To run HazImp from a configuration file do;::

     python hazimp.py -c wind_v1.yaml

Use -c to specify the configuration file.

HazImp can also be ran in parallel, using mpirun.  For example;::

     mpirun -np 4 python hazimp.py -c wind_v1.yaml
     
To run a wind example do;::

     cd examples/wind
     python ../../core_hazimp/hazimp.py  -c wind_v1.yaml

Templates
---------

The simplest way to use HazImp is with a template. There is currently a wind
template.  Templates take into account internal vulnerability curves and the
data flow needed to produce loss information.


Wind Template
-------------
Given gust information from TCRM and point exposure data the loss associated
with 
each site is calculated using the wind template.
The wind vulnerability functions That are used are built-in to HazImp. They are
defined in the GA internal report 

Here is the example wind configuration file (from examples/wind), which uses the wind template.::

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
    This section describes how to load the exposure data. It has 3 sub-sections;

    *file_name*
        The name of the csv exposure file to load. The first row of the csv file is the title row.
    
    *exposure_latitude*
        The title of the csv column with latitude values.

    *exposure_longitude*
        The title of the csv column with longitude values.

*load_wind_ascii*
    A list of ascii grid wind hazard files to load or a single file.  The file
    format is grid ascii.  The values in the file must be *0.2s gust at 10m
    height m/s*, since that is the axis of the HazImp wind vulnerability curves.

*save*
    The file where the results will be saved.  All the results to calculate the
    damage due to the wind hazard are saved to file. The above example saves to
    a csv file, since the file name ends in *.csv*.  This has the disadvantage
    of averaging data from multiple wind hazards.  The information can also be
    saved as numpy arrays.  This can be done by using the *.npz* extension.
    This data can be accessed using Python scripts and is not averaged.
    
    
Without Templates
----------------- 



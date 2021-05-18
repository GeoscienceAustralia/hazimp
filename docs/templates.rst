.. _templates:

Templates
---------

The simplest way to use HazImp is with a template, which sets up a
:class:`PipeLine` to run a collection of :class:`Job` functions. There is currently
a wind template and a flood template. Templates take into account internal 
vulnerability curves and the data flow needed to produce loss information,
simplifying the configuration file.

Templates are used to set out the flow of processing invoked in separate
:class:`Job` functions that are then connected into a :class:`PipeLine` that is
subsequently executed.

.. NOTE:: 
  Because some of the :class:`Job` functions in the templates are essential, the
  order of key/value pairs in the configuration files is important. The code
  will raise a `RuntimeError` if the order is incorrect, or if a mandatory
  configuration key is missing. This is even more important if not using the
  pre-defined templates.


We take the example of the `wind_v4` template. It sets up the following job
sequence in a specific order::

#. LOADCVSEXPOSURE - load the exposure data
#. LOADRASTER - load the wind raster data
#. LOADXMLVULNERABILITY - load the vulnerability functions
#. SIMPLELINKER - select a group of vulnerability functions - some vulnerability files may have multiple sets of curves identified by `vulnerabilitySetID`
#. SELECTVULNFUNCTION - link the selected vulnerability function set (specified by the `vulnerabilitySetID` option) to each exposure asset
#. LOOKUP - do a table lookup to determine the damage index for each asset, based on the intensity measure level (i.e. the wind speed)
#. CALCSTRUCTLOSS - combine the calculated damage index with the building value to calculate $$$ loss
#. SAVE - should speak for itself - saves the building level loss data
#. SAVEPROVENANCE - saves provenance data (like the version of HazImp, source of the hazard data, etc.)

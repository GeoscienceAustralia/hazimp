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
#. LOADRASTER - load the hazard raster data
#. LOADXMLVULNERABILITY - load the vulnerability functions
#. SIMPLELINKER - select a group of vulnerability functions - some vulnerability files may have multiple sets of curves identified by `vulnerabilitySetID`
#. SELECTVULNFUNCTION - link the selected vulnerability function set (specified by the `vulnerabilitySetID` option) to each exposure asset
#. LOOKUP - do a table lookup to determine the damage index for each asset, based on the intensity measure level (e.g. the wind speed)
#. CALCSTRUCTLOSS - combine the calculated damage index with the building value to calculate $$$ loss
#. SAVE - should speak for itself - saves the building level loss data
#. SAVEPROVENANCE - saves provenance data (like the version of HazImp, source of the hazard data, etc.)


Available templates
-------------------

There are currently 6 templates pre-packaged with HazImp (plus one deprecated
template). Most are built around wind impacts, but there are also templates for
earthquake and flood (both structural and contents losses).

#. 'wind_v3' - (DEPRECATED) a basic wind impact template for structural loss and
structural loss ratio.
#. 'wind_v4' - Base wind impact template. Allows user to specify the
vulnerability function set in the configuration.
#. 'wind_v5' - Optional categorisation and tabulation of output data.
#. 'wind_nc' - Includes option to permute exposure data for mean and upper limit
of impact (structural loss ratio).
#. 'earthquake_v1' - Base earthquake impact template. Allows similar functions
(aggregation, permutation, etc.) to the wind_nc template.
#. 'flood_fabric_v2' - calculate structural loss due to flood inundation.
#. 'flood_contents_v2' - contents loss due to flood inundation.
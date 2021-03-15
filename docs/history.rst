.. _history:

History
=======

1.0.0 (2021-03-12)
------------------

* Add provenance records
* Add categorisation, tabulation and aggregation
* Implemented AWS S3 download and upload funcitonality. Also allow the configuration file to be stored on S3 as well. 
* Update hazimp-tests.yml - add coveralls, remove flake8 and pytest install
* Calculate percentages of assets in damage state tabulation
* Updates to documentation (user guide and in-code)
* Add NRML schema from https://github.com/gem/oq-nrmllib/tree/master/openquake/nrmllib/schema
* Validate xml-format vulnerability files prior to execution
* Add support for configuring choropleth aggregation fields via the configuration file
* Add aggregation functions to provenance statement
* Add support for generic 'hazard_raster' to wind templates
* Switched template instantiation to use config dictionary, removed use of config list
* Update find_attributes to use config dictionary for locating attributes, and support lookup via a ordered list of keys to ease deprecation
* add domestic eq vulnerability curves in MMI (#35)
* Increase unit test coverage (#36)
* Update to NRML 0.5 schema
* Add EQ template and example
* Split templates into new module separated by hazard type
* Enable hazard_raster attribute_label to be configured
* Improve memory usage for large raster input: No longer reads the entire raster into memory, reads only the cells defined in the exposure data, removed the ability to pass an in-memory array via 'from_array' and added a 'ThreadPoolExecutor' for some performance improvement when reading hazard data for large exposure datasets
* Change default aggregate output format to GeoJSON (#42)


0.6 (2020-08-13)
----------------

* WIP: First steps on provenance - Initially only implemented in the wind_nc and wind_v5 templates, but several of the jobs include provenance statements
* Add provenance for aggregation file
* Add categorisation and tabulation (pivot table)
* Adding some basic documentation for new functions
* Add updated v5 template
* Template file for tcimpact processing
* WIP: PEP8 conformance
* TCRM-47: Implemented S3 download and upload functionality.
* TCRM-47: Allow config file to be from S3 as well.
* TCRM-88: Moving logger.INFO output to stdout from stderr. Fixed compiler warning.
* Documentation updates
* TCRM-90: Reduce memory usage which require 2 times memory for source and destination arrays. (#18)
* Set raster dtype to GDT_Float32: May not necessarily always be correct, however the previous default was integer which worked for the test cases, except when replacing missing values with `numpy.NaN` (which is ostensibly a float value).
* Fix unittest suite by mocking prov module: Patching various methods under `prov.model.ProvDocument` to allow the test suite to run without error. The tests set up a dummyy context, but missed the provenance module, so we're using `mock` to patch the methods that are called in some tests.


0.5 (2020-07-09)
----------------

* Implement S3 access


0.4 (2020-06-29)
----------------

* Provenance tracking and aggregation added
.. _aggregate:

Saving to geospatial formats
----------------------------

Data can optionally be saved to a geospatial format that aggregates the impact
data to spatial regions (for example suburbs, post codes). 

*aggregate*
    This will activate the option to save to a geospatial format.

    *boundaries* 
        The path to a geospatial file that contains polygon features to aggregate by
    *filename* 
        The path to the output geospatial file. This can be either an ESRI shape
        file (extension `shp`), a GeoJSON file (`json`) or a GeoPackage
        (`gpkg`). If an ESRI shape file is specified, the attribute names are
        modified to ensure they are not truncated. Multiple filenames can be
        specified in a list format.
    *impactcode*
        The attribute in the exposure file that contains a unique code for each
        geographic region to aggregate by.
    *boundarycode*
        The attribute in the `boundaries` file that contains the same unique
        code for each geographic region. Preferably the `impactcode` and
        `boundarycode` will be of the same type (e.g. `int` or `str`)
    *categories*
        If True, and the :ref:`Categorise <categorise>` job is included in the pipeline, the
        number of assets in each damage state defined by the categories will be added as an attribute to the output
        file for each geographic region. **Note the different spelling used in this section.**

Presently, HazImp will aggregate the following fields::

    'structural': 'mean', 'min', 'max'
    'contents': 'mean', 'min', 'max'

If :ref:`permutation <permutation>` of the exposure is performed, then the corresponding
'_max' field can also be included in the aggregation::

    'structural_max': 'mean', 'min', 'max'


Example::

 - aggregate:
     boundaries: QLD_Mesh_Block_2016.shp
     filename: QLD_MeshblockImpacts.shp
     impactcode: MB_CODE
     boundarycode: MB_CODE16
     categories: True
     fields:
      structural: [ mean ]

Output data to multiple files::

 - aggregate:
   boundaries: northwestcape_meshblocks.geojson
   boundarycode: MB_CODE11
   impactcode: MESHBLOCK_CODE_2011
   filename: [olwyn_impact.shp, olwyn_impact.json]
   categories: True
   fields:
      structural: [mean]

.. NOTE::
    The length of some attribute names exceeds the maximum length allowed for
    ESRI shape files and will be automatically truncated when saving to that
    format. A warning message will be generated indicating this truncation is
    being applied.

Aggregate with permuted exposure::

 - aggregate:
   boundaries: northwestcape_meshblocks.geojson
   boundarycode: MB_CODE11
   impactcode: MESHBLOCK_CODE_2011
   filename: [olwyn_impact.json]
   categories: True
   fields:
      structural: [mean]
      structural_max: [mean]



Not all templates include this option. Check before adding the jobs to the 
configuration file.

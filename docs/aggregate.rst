.. _aggregate:

Saving to geospatial formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        If True, and the :ref:`categorise` job is included in the pipeline, the
        number of assets in each damage state defined by the :ref:`categorise`,
        in each geographic region, will be added as an attribute to the output
        file. **Note the different spelling used in this section.**

Presently, HazImp will aggregate the following fields::

    'structural_loss_ratio': 'mean', 'min', 'max'
    'contents_loss_ratio': 'mean', 'min', 'max'


Example::

 - aggregate:
     boundaries: QLD_Mesh_Block_2016.shp
     file_name: QLD_MeshblockImpacts.shp
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


This option has only been implemented in the ``wind_nc`` and ``wind_v5``
templates at this time (June 2020).



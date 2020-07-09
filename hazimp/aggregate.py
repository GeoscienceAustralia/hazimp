"""
Aggregating impact data into a chloropleth map.
"""
import os
import sys
import logging


import pandas
import geopandas

LOGGER = logging.getLogger(__name__)

# List of possible drivers for output:
# See `import fiona; fiona.supported_drivers for a complete list of
# options, but we've only implemented a few to start with.
DRIVERS = {'shp': 'ESRI Shapefile',
           'json': 'GeoJSON',
           'gpkg': 'GPKG'}


def chloropleth(impactfile, shapefile, impactcode, shapecode, outputfile):
    """
    :param str impactfile: Output csv file
    :param str shapefile: Geospatial boundaries to use for aggregation
    :param str impactcode: Field name in the `impactfile` that contains the id
                           for each geospatial region. This is taken from the
                           input exposure file
    :param str shapecode: Field name in the `shapefile` that contains the id
                          for each geospatial region
    :param str outputfile: Destination geospatial file
    """

    left, right = mergefield = impactcode, shapecode

    impact = pandas.read_csv(impactfile)

    # TODO: Consider what fields are essential and what can be
    # removed.
    report = {'REPLACEMENT_VALUE': 'sum',
              'structural_loss_ratio': 'mean',
              '0.2s gust at 10m height m/s': 'max'}

    aggregate = impact.groupby(left).agg(report)

    shapes = geopandas.read_file(shapefile)

    try:
        shapes['key'] = shapes[right].astype(int)
    except KeyError:
        LOGGER.error(f"{shapefile} does not contain an attribute {right}")
        sys.exit(1)

    result = shapes.merge(aggregate, left_on='key', right_index=True)
    driver = DRIVERS[os.path.splitext(outputfile)[1].replace('.', '')]
    if driver == 'ESRI Shapefile':
        LOGGER.info("Changing field names")
        # Need to modify the field names, as ESRI truncates them
        cols = {'REPLACEMENT_VALUE': 'REPVAL',
                'structural_loss_ratio': 'slr_mean',
                '0.2s gust at 10m height m/s': 'maxwind'}
        result = result.rename(columns=cols)

    result.to_file(outputfile, driver=driver)

"""
Aggregating impact data into a chloropleth map.
"""
import os
import sys
import logging


import geopandas

LOGGER = logging.getLogger(__name__)

# List of possible drivers for output:
# See `import fiona; fiona.supported_drivers for a complete list of
# options, but we've only implemented a few to start with.
DRIVERS = {'shp': 'ESRI Shapefile',
           'json': 'GeoJSON',
           'gpkg': 'GPKG'}


def chloropleth(dframe, boundaries, impactcode, bcode, filename):
    """
    Aggregate to geospatial boundaries and save to file

    :param dframe: `pandas.DataFrame` containing point data to be aggregated
    :param str boundaries: File name of a geospatial dataset that contains
                  geographical boundaries to serve as aggregation boundaries
    :param str impactcode: Field name in the `dframe` to aggregate by
    :param str bcode: Corresponding field name in the geospatial dataset.
    :param str filename: Destination filename. Must have a valid extension from
    `shp`, `json` or `gpkg`. See `import fiona; fiona.supported_drivers` for a
    complete list of options, but at this time only three have been
    implemented.
    """

    left, right = impactcode, bcode

    # TODO: Consider what fields are essential and what can be
    # removed.
    # TODO: Change to a function argument and configuration option
    report = {'REPLACEMENT_VALUE': 'sum',
              'structural_loss_ratio': 'mean',
              '0.2s gust at 10m height m/s': 'max'}

    aggregate = dframe.groupby(left).agg(report)

    shapes = geopandas.read_file(boundaries)

    try:
        shapes['key'] = shapes[right].astype(int)
    except KeyError:
        LOGGER.error(f"{boundaries} does not contain an attribute {right}")
        sys.exit(1)

    result = shapes.merge(aggregate, left_on='key', right_index=True)
    driver = DRIVERS[os.path.splitext(filename)[1].replace('.', '')]
    if driver == 'ESRI Shapefile':
        LOGGER.info("Changing field names")
        # Need to modify the field names, as ESRI truncates them
        colnames = {'REPLACEMENT_VALUE': 'REPVAL',
                    'structural_loss_ratio': 'slr_mean',
                    '0.2s gust at 10m height m/s': 'maxwind'}
        result = result.rename(columns=colnames)
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        LOGGER.warning(f"{dirname} does not exist - trying to create it")
        os.makedirs(dirname)
    result.to_file(filename, driver=driver)


"""
bins = [0.0, 0.02, 0.1, 0.2, 0.5, 1.0]
labels = ['Negligible', 'Slight', 'Moderate', 'Extensive', 'Complete']
categorise(bins, labels, 'damage_state')
aggds = df.groupby(['SA1_CODE', 'damage_state'])
aggds.size().to_frame('count').unstack()

"""

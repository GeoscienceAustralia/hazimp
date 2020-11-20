"""
Aggregating impact data into a chloropleth map.
"""
import os
from os.path import abspath, isdir, dirname
import sys
import logging

import numpy as np


import geopandas

LOGGER = logging.getLogger(__name__)

# List of possible drivers for output:
# See `import fiona; fiona.supported_drivers for a complete list of
# options, but we've only implemented a few to start with.
DRIVERS = {'shp': 'ESRI Shapefile',
           'json': 'GeoJSON',
           'geojson': 'GeoJSON',
           'gpkg': 'GPKG'}

COLNAMES = {'REPLACEMENT_VALUE': 'REPVAL',
            'structural_loss_ratio': 'slr_mean',
            '0.2s gust at 10m height m/s': 'maxwind',
            'Damage state': 'dmgstate'}


def choropleth(dframe, boundaries, impactcode, bcode, filename, categories):
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
    :param boolean categories: Add columns for the number of buildings in each
    damage state defined in the 'Damage state' attribute.

    NOTE:: presently, using `categories`=True will not do any categorisation of
    the mean damage index for the aggregation areas.

    """

    left, right = impactcode, bcode

    # TODO: Consider what fields are essential and what can be
    # removed.
    # TODO: Change to a function argument and configuration option
    report = {'structural_loss_ratio': 'mean'}

    aggregate = dframe.groupby(left).agg(report).reset_index()

    if categories and ('Damage state' in dframe.columns):
        dsg = dframe.pivot_table(index=left, columns='Damage state',
                                 aggfunc='size', fill_value=0)
        aggregate = aggregate.merge(dsg, on=left).set_index(left)

    shapes = geopandas.read_file(boundaries)

    try:
        shapes['key'] = shapes[right].astype(np.int64)
    except KeyError:
        LOGGER.error(f"{boundaries} does not contain an attribute {right}")
        sys.exit(1)
    except OverflowError:
        LOGGER.error(f"Unable to convert {right} values to ints")
        sys.exit(1)

    result = shapes.merge(aggregate, left_on='key', right_index=True)
    fileext = os.path.splitext(filename)[1].replace('.', '')
    try:
        driver = DRIVERS[fileext]
    except KeyError:
        LOGGER.error(f"Unknown output extension: {fileext}")
        LOGGER.error("No aggregation will be saved")
        return

    if driver == 'ESRI Shapefile':
        LOGGER.info("Changing field names")
        # Need to modify the field names, as ESRI truncates them
        result = result.rename(columns=COLNAMES)
    directory = dirname(abspath(filename))
    if not os.path.isdir(directory):
        LOGGER.warning(f"{directory} does not exist - trying to create it")
        os.makedirs(directory)
    try:
        result.to_file(filename, driver=driver)
    except ValueError:
        LOGGER.error(f"Cannot save aggregated data")
        LOGGER.error("check fields used to link aggregation boundaries")


"""
bins = [0.0, 0.02, 0.1, 0.2, 0.5, 1.0]
labels = ['Negligible', 'Slight', 'Moderate', 'Extensive', 'Complete']
categorise(bins, labels, 'damage_state')
aggds = df.groupby(['SA1_CODE', 'damage_state'])
aggds.size().to_frame('count').unstack()

"""

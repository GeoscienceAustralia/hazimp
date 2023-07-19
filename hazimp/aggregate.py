"""
Aggregating impact data into a chloropleth map.
"""
import logging
import os
import sys
from os.path import abspath, isdir, dirname

import geopandas
import pandas as pd
import numpy as np

LOGGER = logging.getLogger(__name__)

# List of possible drivers for output:
# See `import fiona; fiona.supported_drivers for a complete list of
# options, but we've only implemented a few to start with.
DRIVERS = {'shp': 'ESRI Shapefile',
           'json': 'GeoJSON',
           'geojson': 'GeoJSON',
           'gpkg': 'GPKG'}

# These are replacement names for use when writing ESRI shape files that have a
# limited length for the attribute name (10-bytes)
# TODO: Labels for other hazard measures, damage measures, etc.
COLNAMES = {'REPLACEMENT_VALUE': 'REPVAL',
            '0.2s gust at 10m height m/s': 'maxwind',
            'Damage state': 'dmgstate'}

# Loss categories to rename
loss_categories = [
    {'label': 'slr', 'identifiers': ['structural', 'structural_loss_ratio']},
    {'label': 'clr', 'identifiers': ['contents', 'contents_loss_ratio']}
]

# Supported Pandas aggregate functions
aggregate_functions = ['mean', 'min', 'max']

# Generate replacement labels for loss categories
for function in aggregate_functions:
    for loss_category in loss_categories:
        for identifier in loss_category['identifiers']:
            aggregate_label = f'{identifier}_{function}'
            category_label = f'Damage state ({aggregate_label})'

            COLNAMES[aggregate_label] = f'{loss_category["label"]}_{function}'
            COLNAMES[category_label] = f'ds_{function}'


def choropleth(dframe, boundaries, impactcode, bcode, filename,
               fields, categories, categorise) -> bool:
    """
    Aggregate to geospatial boundaries using joins on attributes and save to
    file.

    :param dframe: `pandas.DataFrame` containing point data to be aggregated
    :param str boundaries: File name of a geospatial dataset that contains
                  geographical boundaries to serve as aggregation boundaries
    :param str impactcode: Field name in the `dframe` to aggregate by
    :param str bcode: Corresponding field name in the geospatial dataset.
    :param str filename: Destination file name. Must have a valid extension of
                         `shp`, `json` or `gpkg`.
                         See `import fiona; fiona.supported_drivers` for a
                         complete list of options, but at this time only three
                         have been implemented.
    :param boolean categories: Add columns for the number of buildings in each
                               damage state defined in the 'Damage state'
                               attribute. This requires that a 'categorise`
                               job has been included in the pipeline, which in
                               turn requires the bins and labels to be defined
                               in the job configuration.
    :param dict categorise: categorise job attributes

    NOTE::

        Presently, using `categories`=True will not do any categorisation of
        the mean damage index for the aggregation areas.

    :param dict fields: A `dict` with keys of valid column names (from the
                        `DataFrame`) and values being lists of aggregation
                        functions to apply to the columns.

    For example::

        fields = {'structural': ['mean']}

    See
    https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#aggregation
    for more guidance on using aggregation with `DataFrames`
    """

    left, right = impactcode, bcode

    aggregate = dframe.groupby(left).agg(fields).reset_index()
    aggregate.columns = [
        '_'.join(columns).rstrip('_') for columns in aggregate.columns.values
    ]

    field_name = categorise['field_name'] if categorise else 'Damage state'

    if categories and categorise:
        aggregate_categorisation(aggregate, categorise, fields, field_name)

    if categories and (field_name in dframe.columns):
        dsg = dframe.pivot_table(index=left, columns=field_name,
                                 aggfunc='size', fill_value=0)
        aggregate = aggregate.merge(dsg, on=left).set_index(left)
    elif categories and (field_name not in dframe.columns):
        LOGGER.warning("No categorisation will be performed")
        aggregate.set_index(left, inplace=True)
    else:
        aggregate.set_index(left, inplace=True)

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
        return False

    if driver == 'ESRI Shapefile':
        LOGGER.info("ESRI shape file output - changing field names")
        # Need to modify the field names, as ESRI truncates them
        result = result.rename(columns=COLNAMES)
    directory = dirname(abspath(filename))
    if not isdir(directory):
        LOGGER.warning(f"{directory} does not exist - trying to create it")
        os.makedirs(directory)
    try:
        result.to_file(filename, driver=driver)
        return True
    except ValueError:
        LOGGER.error("Cannot save aggregated data")
        LOGGER.error("Check fields used to link aggregation boundaries")
        return False


def aggregate_categorisation(aggregate, categorise: dict,
                             fields: dict, field_name: str):
    """
    Categorise aggregated field values into discrete intervals.

    :param aggregate: `pandas.DataFrame` containing aggregated data
    :param categorise: categorise job attributes
    :param fields: fields to aggregate
    :param field_name: name of categorised column
    """
    columns_to_aggregate = []

    for (field, functions) in fields.items():
        for func in functions:
            column = f'{field}_{func}'
            if column in aggregate:
                columns_to_aggregate.append(column)

    detailed_labels = len(columns_to_aggregate) > 1

    for column in columns_to_aggregate:
        label = f'{field_name} ({column})' if detailed_labels else field_name

        aggregate[label] = pd.cut(
            aggregate[column],
            categorise['bins'],
            right=False,
            labels=categorise['labels']
        ).astype('str')


def aggregate_loss_atts(dframe, groupby=None, kwargs=None):
    """
    Aggregate the impact data contained in a `pandas.DataFrame`

    :param dframe: `pandas.DataFrame` that contains impact data
    :param str groupby: A column in the `DataFrame` that corresponds to
            regions by which to aggregate data
    :param dict kwargs: A `dict` with keys of valid column names (from the
            `DataFrame`) and values being lists of aggregation functions to
            apply to the columns.

    For example::

        kwargs = {'REPLACEMENT_VALUE': ['mean', 'sum'],
                'structural': ['mean', 'std']}

    See
    https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#aggregation
    for more guidance on using aggregation with `DataFrames`

    :returns: A `pandas.GroupBy` object.

    """
    try:
        grouped = dframe.groupby(groupby, as_index=False)
    except KeyError:
        LOGGER.exception(f"No field named {groupby} in the exposure data")
        sys.exit(1)
    outdf = grouped.agg(kwargs)

    outdf.columns = ['_'.join(col).rstrip('_') for col in outdf.columns.values]
    outdf.reset_index(col_level=1)
    outdf.columns = outdf.columns.get_level_values(0)
    return outdf

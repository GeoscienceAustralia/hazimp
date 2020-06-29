.. _categorise: 

Including categorisations
=========================

Users may want to convert from numerical values to categorical values for output
fields. For example, converting the structural loss ratio from a value between 0
and 1 into categories which are more descriptive (see the table below).

+-------------+--------------+------------+
| Lower value | Uppper value | Category   |
+=============+==============+============+
| 0           | 0.02         | Negligible |
+-------------+--------------+------------+
| 0.02        | 0.1          | Slight     |
+-------------+--------------+------------+
| 0.1         | 0.2          | Moderate   |
+-------------+--------------+------------+
| 0.2         | 0.5          | Extensive  |
+-------------+--------------+------------+
| 0.5         | 1.0          | Complete   |
+-------------+--------------+------------+

The `Categorise` job enables users to do this categorisation. Add the
"categorise" section to the configuration file to run this job. This is based on
`pandas.cut`

*categorise* 
    This will enable the `Categorise` job. The job requires the following
    options to be set.

    *field_name* 
        The name of the created (categorical) field in the `context.exposure_att`
        `DataFrame`

    *bins*
        Monotonically increasing array of bin edges, including the rightmost edge,
        allowing for non-uniform bin widths.

    *labels*
        Specifies the labels for the returned bins. Must be the same length as the
        resulting bins.

Example
-------

A basic example, which would result in the categories listed in the table above
being added to the column "Damage state": 

.. code:: yaml

 - categorise:
    field_name: 'Damage state'
    bins: [0.0, 0.02, 0.1, 0.2, 0.5, 1.0]
    labels: ['Negligible', 'Slight', 'Moderate', 'Extensive', 'Complete']


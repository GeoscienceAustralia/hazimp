.. _tabulate:

Generate tables
===============

A common way of reporting the outcomes of a HazImp analysis is to look at the
number of features distributed across various ranges. For example, the number of
buildings in a given damage state, grouped by an age category. While many may
want to do their own pivot tables on the output, this can automate the process
for the most common index/column combination.

+------------------+------------+--------+----------+-----------+----------+
| Construction era | Negligible | Slight | Moderate | Extensive | Complete |
+==================+============+========+==========+===========+==========+
|   1914 -   1946  | 9542       | 311    | 25       | 46        | 7        |
+------------------+------------+--------+----------+-----------+----------+
|    1947 - 1961   | 10496      | 113    | 11       | 1         | 0        |
+------------------+------------+--------+----------+-----------+----------+
|    1962 - 1981   | 23984      | 909    | 73       | 57        | 8        |
+------------------+------------+--------+----------+-----------+----------+
|    1982 - 1996   | 25676      | 914    | 186      | 39        | 1        |
+------------------+------------+--------+----------+-----------+----------+
| 1997 -   present | 16675      | 711    | 115      | 40        | 3        |
+------------------+------------+--------+----------+-----------+----------+

The `Tabulate` job performs a pivot table operation on the
`context.exposure_att` `DataFrame` and writes the results to an Excel file. Add
the "tabulate" section to the configuration file to run this job. This is
closely based on `pandas.DataFrame.pivot_table`.

*tabulate*
    Run a tabulation job

    *file_name*
        Destination for the output of the tabulation. Should be an Excel file

    *index*
        Keys to group by on the pivot table index.  If a list is passed,
        it is used as the same manner as column values.

    *columns*
        Keys to group by on the pivot table column.  If a list is passed,
        it is used as the same manner as column values.

    *aggfunc*
        function, list of functions, dict, default numpy.mean
        If a list of functions passed, the resulting pivot table will have
        hierarchical columns whose top level are the function names
        (inferred from the function objects themselves)
        If dict is passed, the key is column to aggregate and value
        is function or list of functions.


Examples
--------

.. code:: yaml

 - tabulate:
    file_name: wind_impact_by_year.xlsx
    index: YEAR_BUILT
    columns: Damage state
    aggfunc: size

This will return a table of the number (the `size` function) of buildings in each damage state,
grouped by the "YEAR_BUILT" attribute, and saved to the file "wind_impact_by_year.xlsx"

.. code:: yaml

 - tabulate:
    file_name: mean_slr_by_year.xlsx
    index: YEAR_BUILT
    columns: structural_loss_ratio
    aggfunc: mean

This will return a table of the mean structural loss ratio of buildings, grouped
by the "YEAR_BUILT" attribute, and saved to the file "mean_slr_by_year.xlsx"



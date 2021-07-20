.. _permutation:

Using permutation to understand uncertainty in vulnerability
============================================================

In many regions (in Australia), the attributes of individual buildings are 
unknown, but are recorded for some statistical area (e.g. suburb, local 
government area). In this case, the vulnerability curve assigned to a 
building may not be precisely determined, which can lead to uncertainty 
in the impact for a region.

To overcome this, users can run the impact calculation multiple times, 
while permuting the vulnerability curves for each region (suburb, local 
government area, etc.). This requires some additional entries in the 
template file.

*exposure_permutation*
    This describes the :ref:`exposure`_ attribute that will constrain the 
    permutation, and the number of permuations.
    
    *groupby*
    The field name in the :ref:`exposure`_ data by which the assets will be grouped.

    *iterations* 
    The number of iterations to perform. Default is 1000 iterations

    *quantile*
    The quantile to represent the "worst-case" result. Default=0.95 (95th percentile)

Example::

 - exposure_permutation:
     groupby: MB_CODE
     iterations: 1000


The resulting output calculates a mean loss per building from all permutations,
as well as a "worst-case" loss, which is the permutation that provides the
highest mean loss over all buildings. In reality, we actually use the 95th
percentile of the mean loss to determine the "worst-case" event. The values are
stored in an attribute with the suffix '_max' appended.

An example of aggregation to geospatial fomats using permutation is given in the
:ref:`aggregate`_ section.

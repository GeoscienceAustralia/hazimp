.. _exposure:

Exposure data
=============

Exposure data provides details of the assets (e.g. buildings) for which the
impacts will be calculated. As a minimum, the exposure data needs to include
geographic location data (latitude and longitude), a unique identifier for each
asset, and an attribute that indicates which vulnerability function to use for
that asset. 

Additional attributes can enable a more detailed analysis - for example,
aggregation based on specific attributes. For example, including an attribute of
the construction era would allow aggregation by that attribute. In the case of
using `permutation <permutation>`_, the exposure data must include an attribute that
indicates the geographic region over which the permutation will be performed. 


Example
-------

At it's most basic level, the following table has sufficient attributes to be
used by HazImp for a wind impact calculation:

+----+----------+-----------+--------------------------------+-------------------+
| ID | Latitude | Longitude | WIND_VULNERABILITY_FUNCTION_ID | REPLACEMENT_VALUE |
+====+==========+===========+================================+===================+
| 1  | -22.99   | 120.01    |               dw1              |                 1 |
+----+----------+-----------+--------------------------------+-------------------+
| 2  | -23.01   | 121.99    |               dw2              |                10 |
+----+----------+-----------+--------------------------------+-------------------+
| 3  | -22.99   | 122.01    |               dw4              |               100 |
+----+----------+-----------+--------------------------------+-------------------+
| 4  | -23.99   | 122.01    |               dw7              |              1000 |
+----+----------+-----------+--------------------------------+-------------------+
| 5  | -23      | 123.01    |              dw306             |             10000 |
+----+----------+-----------+--------------------------------+-------------------+

Using this data, the configuration file needs to specify which attribute
indicates the latitude and longitude of the assets using the *exposure_latitude*
and *exposure_longitude* elements.

.. code:: yaml

 - load_exposure:
    file_name: <exposure.csv>
    exposure_latitude: Latitude
    exposure_longitude: Longitude
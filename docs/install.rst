Installing HazImp
=================

Dependencies
------------

HazImp relies on python and additional libraries.

There are several alternatives for suitable python environments.

Conda
^^^^^
Using conda helps to avoid version conflicts between different python packages
and other dependencies. Download (wget) and install miniconda. 
Create a new environment with a command such as::

  conda create -n haz python=2.7 numpy scipy pandas gdal shapely matplotlib basemap basemap-data-hires pyyaml netcdf4 statsmodels seaborn coverage pep8 pylint nose jupyter ipython geopandas jupyter ipython geopandas cartopy

Before each session, remember to activate the corresponding environment, 
e.g. `conda activate haz`.

User install using system python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On some systems (e.g. rhe-compute1) the existing system python installation may be made suitable.::

  for x in pep8 coverage pyyaml pylint pandas ; do pip install --user $x ; done

On MS-Windows::

  for %x in (pep8, coverage, pyyaml, pylint, pandas) do pip install --user %x

System python install
^^^^^^^^^^^^^^^^^^^^^

On Ubuntu systems, the following requires system administrator privileges.::

  sudo apt-get install python-numpy, python-scipy
  sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint, pandas, nose

Getting the code
----------------

Download the HazImp source from GitHub.

You can either download a zip file containing
the HazImp code, or clone the repository (if you have `git`
installed) as follows:

Using ssh:: 
  
  git clone git@github.com:GeoscienceAustralia/hazimp.git

Using HTTPS::
  
  git clone https://github.com/GeoscienceAustralia/hazimp

Install HazImp
--------------

Install HazImp into your python environment::

  python setup.py install

Or, if you are interested in modifying HazImp, the following alternative
install command will instead provide your python environment with links to
the location where you have downloaded the HazImp source::
 
  python setup.py develop

To use HazImp, run `hazimp --help` from the command line.
You can also verify the code using `./run_tests`.


Testing the installation
------------------------

Users can test the installation with the :command:`run_tests`
script. This depends on the `nose` and `coverage` libraries for
Python. The :command:`run_tests` script is a shell script, so needs to
be executed in a shell (e.g. `bash`, `sh` or `csh`).

On a Windows command line::
  
  nosetests hazimp/ --with-doctest --cover-package=hazimp --with-xunit --xunit-file='nosetests.xml' --nocapture



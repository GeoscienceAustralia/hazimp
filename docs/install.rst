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

  conda create -f hazimp.yml 

Before each session, remember to activate the corresponding environment, 
e.g. `conda activate hazimp`.

User install using system python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On some systems the existing system python installation may be made suitable.::

  for x in pep8 coverage pyyaml pylint pandas prov pydot; do pip install --user $x ; done

On MS-Windows::

  for %x in (pep8, coverage, pyyaml, pylint, pandas, prov, pydot) do pip install --user %x

System python install
^^^^^^^^^^^^^^^^^^^^^

On Ubuntu systems, the following requires system administrator privileges.::

.. code-block:: bash

  sudo apt-get install python-numpy, python-scipy
  sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint, pandas, nose, prov, pydot

Getting the code
----------------

Download the HazImp source from GitHub.

You can either download a zip file containing
the HazImp code, or clone the repository (if you have `git`
installed) as follows:

Using ssh:: 

.. code-block:: bash

  git clone git@github.com:GeoscienceAustralia/hazimp.git

Using HTTPS::

.. code-block:: bash

  git clone https://github.com/GeoscienceAustralia/hazimp

Install HazImp
--------------

Install HazImp into your python environment::

.. code-block:: bash
  python setup.py install

Or, if you are interested in modifying HazImp, the following alternative
install command will instead provide your python environment with links to
the location where you have downloaded the HazImp source::

.. code-block:: bash
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



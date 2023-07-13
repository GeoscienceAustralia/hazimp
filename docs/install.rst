Installing HazImp
=================

Getting the code
----------------

Download the HazImp source from GitHub.

You can either download a zip file containing
the HazImp code, or clone the repository (if you have `git`
installed) as follows:

Using ssh:

.. code-block:: bash

  git clone git@github.com:GeoscienceAustralia/hazimp.git

Using HTTPS:

.. code-block:: bash

  git clone https://github.com/GeoscienceAustralia/hazimp

The source code includes a number of files that may help with installing the
package dependencies.

Dependencies
------------

HazImp uses Python and additional libraries.

There are several alternatives for suitable python environments.

conda
^^^^^

We recommend using conda_ to manage dependencies and run HazImp. Using conda
helps to avoid version conflicts between different python packages and other
dependencies. Download (wget) and install miniconda_, then use the conda
environment file `hazimp.yml` included with the software to install the
set of compatible packages. conda_ is available for Linux, MacOS and Windows
environments.

Once you have installed miniconda_, create a new environment with a command such
as:

.. code-block:: bash

  conda env create -f hazimp.yml

Before each session, remember to activate the corresponding environment,
e.g. `conda activate hazimp`.


mamba
^^^^^

Because of the complex set of dependencies, the build time can be quite long.
To get around this, you can use the mamba_ package manager to build the
environment:

.. code-block:: bash

    conda install mamba -n base -c conda-forge
    mamba env create -f hazimp.yml


User install using system python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On some systems the existing system python installation may be made suitable.::

  for x in pep8 coverage pyyaml pylint pandas prov pydot; do pip install --user $x ; done

On MS-Windows::

  for %x in (pep8, coverage, pyyaml, pylint, pandas, prov, pydot) do pip install
  --user %x

NOTE:: This is not the exhaustive list of required packages. See the full list
in `hazimp.yml`.

System python install
^^^^^^^^^^^^^^^^^^^^^

On Ubuntu systems, the following requires system administrator privileges.

.. code-block:: bash

  sudo apt-get install python-numpy, python-scipy
  sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint, pandas, nose, prov, pydot



Install HazImp
--------------

To install HazImp into your python environment, at a command prompt, enter the
following command:

.. code-block:: bash

  python setup.py install

Or, if you are interested in modifying HazImp, the following alternative
install command will instead provide your python environment with links to
the location where you have downloaded the HazImp source:

.. code-block:: bash

  python setup.py develop

Please read the `Contributing code`_ notes if you wish to modify HazImp.

To use HazImp, run `hazimp --help` from the command line.
You can also verify the code using `./run_tests`.


Testing the installation
------------------------

Users can test the installation with the :command:`run_tests`
script. This depends on the `nose` and `coverage` libraries for
Python. The :command:`run_tests` script is a shell script, so needs to
be executed in a shell (e.g. `bash`, `sh` or `csh`).

On a Windows command line::

  nosetests tests/ --with-doctest --cover-package=hazimp --with-xunit --xunit-file=nosetests.xml --nocapture


.. _conda: https://conda.io/en/latest/index.html
.. _miniconda: https://conda.io/en/latest/miniconda.html
.. _mamba: https://mamba.readthedocs.io/en/latest/index.html
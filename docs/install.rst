Installing HazImp
=================


Getting the code
----------------

First download the code. You can either download a zip file containing
the `HazImp` code, or clone the repository (if you have `git`
installed) as follows:

Using ssh:: 
  
  git clone git@github.com:GeoscienceAustralia/hazimp.git

Using HTTPS::
  
  git clone https://github.com/GeoscienceAustralia/hazimp

Dependencies
------------

`HazImp` relies on several additional Python libraries. 

On Ubuntu sytems::

  sudo apt-get install python-numpy, python-scipy
  sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint, pandas, nose


Using pip
---------

Windows users can use `pip` to install and/or update libraries::

  pip install --user pep8
  pip install --user coverage
  pip install --user pyyaml
  pip install --user pylint
  pip install --user pandas
  pip install --user nose
  pip install --user coverage


Environment variables
---------------------

Add the location of the root HazImp directory to PYTHONPATH. e.g. (in .bashrc)::
  
  export PYTHONPATH=$PYTHONPATH:${HOME}/hazimp

Testing the installation
------------------------

Users can test the installation with the :command:`run_tests`
script. This depends on the `nose` and `coverage` libraries for
Python. The :command:`run_tests` script is a shell script, so needs to
be executed in a shell (e.g. `bash`, `sh` or `csh`).

On a Windows command line::
  
  :command:`nosetests hazimp/ --with-doctest --cover-package=hazimp --with-xunit --xunit-file='nosetests.xml' --nocapture` 



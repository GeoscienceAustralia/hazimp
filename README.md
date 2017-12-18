HazImp
======

A Hazard impact assessment tool.

This branch enables users to permute attributes in the exposure database for randomised evaluation of impacts. e.g. one can permute the vulnerability curves assigned to each exposure element in a grouping (such as suburb) to develop a distribution of impact outcomes. 

Requires pandas (provides methods for manipulation of the exposure file).

Install
=======
sudo apt-get install python-numpy, python-scipy
sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint, pandas

Local install on rhe-compute1
=============================

  pip install --user pep8
  pip install --user coverage
  pip install --user pyyaml
  pip install --user pylint
  pip install --user pandas


Environment variables
=====================
Add the location of the root HazImp directory to PYTHONPATH. e.g. (in .bashrc)
export HAZIMPPATH=${HOME}/sandpits/hazimp
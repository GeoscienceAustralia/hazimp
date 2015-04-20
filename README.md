HazImp
======

A Hazard impact assessment tool.

Install
=======
sudo apt-get install python-numpy, python-scipy
sudo apt-get install python-gdal, python-yaml, python-coverage, pep8, pylint

Local install on rhe-compute1
=============================
pip install --user pep8
pip install --user coverage
pip install --user pyyaml
pip install --user pylint


Environment variables
=====================
Add the location of the root HazImp directory to PYTHONPATH. e.g. (in .bashrc)
export HAZIMPPATH=${HOME}/sandpits/hazimp
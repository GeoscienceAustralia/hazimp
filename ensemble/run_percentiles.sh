#!/bin/bash
#PBS -P w85
#PBS -N pc_16_threads
#PBS -m ae
#PBS -M craig.arthur@ga.gov.au
#PBS -lwalltime=1:00:00
#PBS -lmem=64GB,ncpus=16,jobfs=4000MB
#PBS -joe
#PBS -lstorage=gdata/w85+gdata/v10
#PBS -W umask=002

module purge
module load pbs
module load dot

module load python3/3.7.4
module load netcdf/4.6.3
module load hdf5/1.10.5
module load geos/3.8.0
module load proj/6.2.1
module load gdal/3.0.2

# Need to ensure we get the correct paths to access the local version of gdal bindings. 
# The module versions are compiled against Python3.6
export PYTHONPATH=/g/data/w85/.local/lib/python3.7/site-packages:$PYTHONPATH

# Add the local Python-based scripts to the path:
export PATH=/g/data/w85/.local/bin:$PATH

# Needs to be resolved, but this suppresses an error related to HDF5 libs
export HDF5_DISABLE_VERSION_CHECK=2

module list
# Add path to where TCRM is installed.
SOFTWARE=/g/data/w85/software
BRANCH=master

export PYTHONPATH=$PYTHONPATH:$SOFTWARE/tcrm/$BRANCH:$SOFTWARE/tcrm/$BRANCH/Utilities


python3 loss_percentiles.py -l /g/data/w85/kr4383/yasi/impact/low_res -wd /g/data/w85/kr4383/yasi/percentile -wc pm_template.ini -hc hazimp_template.yaml
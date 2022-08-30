#!/bin/bash

# Prepare the LXPLUS path 
source /cvmfs/sft.cern.ch/lcg/views/dev4/latest/x86_64-centos7-gcc11-opt/setup.sh

# Use pipenv to install dependencies
pip install pipenv
pipenv install
pipenv shell

# Install the package
pip install .
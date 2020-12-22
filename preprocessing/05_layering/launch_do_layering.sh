#!/bin/bash

# This script runs do_layering.py for all subjects in parallel in the
# conda environment layerfMRI
# Check python do_layering.py -h for information about the arguments

# initialize the proper environment to run the python script
source activate layerfMRI
echo
echo `conda info | grep "active environment"`
echo
echo

# subjects 1 4 7 have missing data
subjects=(2 3 5 6 8 9 10 11 12 13 14)

printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 12 -I{} python do_layering.py --sub={}

echo
echo

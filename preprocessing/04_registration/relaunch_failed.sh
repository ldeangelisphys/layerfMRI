#!/bin/bash

# This script runs do_registration.py for all subjects in parallel in the
# conda environment layerfMRI
# Check python do_registration.py -h for information about the arguments

# NB: pandoc should be installed on the system by sudo

# initialize the proper environment to run the python script
source activate layerfMRI
echo
echo `conda info | grep "active environment"`
echo
echo

# subjects 1 4 7 have missing data
subjects=(6 9 13 14)

printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 12 -I{} python do_registration.py --sub={} --nThreads=10

echo
echo

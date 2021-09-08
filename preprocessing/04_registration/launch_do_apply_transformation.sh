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

# subjects 1 4 7 have missing data; 8 and 13 were excluded due to high motion,
# incomplete data acquisition and/or inconsistency between fMRI and log files
# evidenced after basic fMRI preprocessing
subjects=(2 3 5 6 9 10 11 12 14)

printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 4 -I{} python do_apply_transformation.py --sub={}

echo
echo

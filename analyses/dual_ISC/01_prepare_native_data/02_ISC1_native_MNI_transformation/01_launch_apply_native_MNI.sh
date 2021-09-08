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

[ $# -lt 3 ] && { echo;
                  printf "\n run with: \n ./01_launch_apply_native_MNI.sh "; \
                  printf " [labelmap_file] [labelmap_stub] [labelmap_folder] \n \n"; \
                  printf " e.g. \n ./01_launch_apply_native_MNI.sh "; \
                  printf " loo_isc_M_OR_S_No001_k50_bin.nii.gz  M_OR_S  ISC \n\n"; \
                  exit 1; }

labelmap_file=$1
labelmap_stub=$2
labelmap_folder=$3


# subjects 1 4 7 have missing data; 8 and 13 were excluded due to high motion,
# incomplete data acquisition and/or inconsistency between fMRI and log files
# evidenced after basic fMRI preprocessing
subject_numba_file=/data00/layerfMRI/Github_repo/layerfMRI/analyses/dual_ISC/list_subjects

subjects=$(<${subject_numba_file})


# apply transformation to depth and atlas
printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 12 -I{} python do_apply_native_MNI.py --sub={} \
                                                       --labelmap_file=${labelmap_file} \
                                                       --labelmap_stub=${labelmap_stub} \
                                                       --labelmap_folder=${labelmap_folder}

echo
echo


# when all is done, cleanup the /tmp, since ANTs leaves a lot of stuff there
# rm -rf `find /tmp -user cerliani`

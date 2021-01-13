#!/bin/bash

# This script runs do_data_preparation.py for all subjects in parallel in the
# conda environment layerfMRI
# Check python do_data_preparation.py -h for information about the arguments

sub_list=/data00/layerfMRI/list_subjects

# initialize the proper environment to run the python script
source activate layerfMRI
echo
echo `conda info | grep "active environment"`
echo
echo

# subjects 1 4 7 8 have missing data
subjects=$(<${sub_list})

printf "%s\n" "${subjects[@]}" | xargs -n 1 -P 12 -I{} python do_data_preparation.py --sub={}

echo
echo


# Generate the average (mean and median) images
regdata_dir=/data00/layerfMRI/regdata

target_dir=${PWD}/data4histograms

for contrast in depth layers; do
  contrast_file=LH_layering_layering-${contrast}_MNIspace.nii.gz
  imlist=`imglob ${regdata_dir}/sub_*/ses_01/anat/layering/${contrast_file}`

  echo ${contrast}
  echo merging all the ${contrast} files in a 4D
  fslmerge -t ${target_dir}/all_${contrast}.nii.gz ${imlist}

  echo calculating the mean image
  fslmaths ${target_dir}/all_${contrast}.nii.gz \
           -Tmean \
           ${target_dir}/mean_${contrast}.nii.gz

  echo calculating the median image
  fslmaths ${target_dir}/all_${contrast}.nii.gz \
           -Tmedian \
           ${target_dir}/median_${contrast}.nii.gz
  echo

done

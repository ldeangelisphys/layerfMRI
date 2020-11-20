#!/bin/bash


# to be run INSIDE the following directory
# /data00/leonardo/layers/regdata/sub_08

startingdir=$PWD

cd /data00/leonardo/layers/regdata/sub_08


# remove previous masks
for i in `find . -name *brain_mask* | grep -E 'task|part'`; do

  rm ${i}

done


for i in `find . -name *bc.nii.gz | grep -E 'task|part'`; do

  # threshold
  tmp=`remove_ext ${i}`
  fslmaths ${tmp} -thr 1e5 ${tmp}_thr

  # create new masks
  3dAutomask -q -prefix ${tmp}_brain_mask.nii.gz ${tmp}_thr.nii.gz
  fslmaths ${tmp}_brain_mask.nii.gz -mul ${tmp}.nii.gz ${tmp}_brain.nii.gz

  # rm temporary thresholded files
  imrm ${tmp}_thr

done



# View the result
for i in `find ~+ -name *bc.nii.gz | grep -E 'task|part'`; do

  tmp=`remove_ext ${i}`
  fslview_deprecated ${tmp} ${tmp}_brain_mask -t 0.3 -l "Red"

done


cd ${startingdir}

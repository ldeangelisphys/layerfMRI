#!/bin/bash

subject_list=$(</data00/layerfMRI/list_subjects)
# printf "%s\n" ${subject_list[@]}

regdata_dir=/data00/layerfMRI/regdata


# Create a function to run all the mean image creation and export it
function do_mean_image() {

  sub=`printf sub_%02d $1`
  # echo launching ${sub}

  fmri4D=($(find ${regdata_dir} -name "*4D_MNI*" | grep ${sub}))
  # printf "%s\n" ${fmri4D[@]}

  for i in ${fmri4D[@]}; do

    tmp_mean_image_run=${sub}_mean_image_`echo ${i} | awk -F/ '{print $NF}'`

    fslmaths ${i} -Tmean ${tmp_mean_image_run}
    echo fatto ${tmp_mean_image_run}

  done

  fslmerge -t ${sub}_allmeans `imglob ${sub}*`
  rm ${sub}*4D*

  fslmaths ${sub}_allmeans -Tmean -thr 0 -bin ${sub}_mean
  imrm ${sub}_allmeans

}

export -f do_mean_image


# For some reason the xargs below does not work, even though the single function
# works. It appears that when running from the script the innner array is completely ignored.
# So I just do it "semi-manually" with multiple calls. Horrible but does the job.

# Run all sub in parallel
# printf "%s\n" "${subject_list[@]}" | xargs -n 1 -P 10 -t -I {} bash -c 'do_mean_image {}'


do_mean_image 2 &
do_mean_image 3 &
do_mean_image 5 &
do_mean_image 6 &
do_mean_image 9 &
do_mean_image 10 &
do_mean_image 11 &
do_mean_image 12 &
do_mean_image 14 &

# Create the frequency map
fslmerge -t allmasks_4D `imglob sub*.nii.gz`

nsub=`fslinfo allmasks_4D.nii.gz | grep ^dim4 | awk '{print $2}'`

fslmaths allmasks_4D -Tmean -mul ${nsub} freq_map_fmri_FOV

# EOF

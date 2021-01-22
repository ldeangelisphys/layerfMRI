#!/bin/bash

# -------------------- USER-DEFINED OPTIONS ---------------------------------


analysis_folder=PPI

numba_cores=10


# -------------------- END of USER-DEFINED OPTIONS --------------------------

datadir=/data00/layerfMRI/regdata
ppidir=/data00/layerfMRI/analyses/${analysis_folder}
design_template=${ppidir}/000_template_design_${analysis_folder}.FSF
fsf_folder=${ppidir}/000_subj_level_feat


# create anew a folder to store the fsf for each subj/task/run
if [ -d ${fsf_folder} ]; then
  rm -rf ${fsf_folder}
fi
mkdir ${fsf_folder}


# subj 8 is fucked up, and 13 either has problems or will be come back later
listsub_fMRI=(2 3 5 6 9 10 11 12 14)


for insub in ${listsub_fMRI[@]}; do

  sub=`printf %02d ${insub}`
  echo sub_${sub}

  for ses in 01 02; do
    for task in 1 2 3 4; do
      for run in 1 2; do

        nii4d=${datadir}/sub_${sub}/ses_${ses}/func/task_${task}_run_${run}_4D_MNI.nii.gz

        if [ -f ${nii4d} ]; then

          dim1=`fslinfo ${nii4d} | grep ^dim1 | awk '{print $2}'`
          dim2=`fslinfo ${nii4d} | grep ^dim2 | awk '{print $2}'`
          dim3=`fslinfo ${nii4d} | grep ^dim3 | awk '{print $2}'`
          dim4=`fslinfo ${nii4d} | grep ^dim4 | awk '{print $2}'`

          totalVoxels=$((dim1*dim2*dim3*dim4))

          fsf_sub=${fsf_folder}/sub_${sub}_task_${task}_run_${run}.fsf

          sed -e "s@OUTPUTFEATDIR@${fsf_folder}/sub_${sub}_task_${task}_run_${run}.feat@g" \
              -e "s@NUMBATIMEPOINTS@${dim4}@g" \
              -e "s@TOTALNUMBAVOXELS@${totalVoxels}@g" \
              -e "s@NII4DMNI@${nii4d}@g" \
              -e "s@EVM@${ppidir}/EV_predictors/sub_${sub}_EV_task_${task}_run_${run}_M.txt@g" \
              -e "s@EVS@${ppidir}/EV_predictors/sub_${sub}_EV_task_${task}_run_${run}_S.txt@g" \
              -e "s@EVPPI@${ppidir}/PPI_predictors/sub_${sub}_task_${task}_run_${run}_4D_MNI_ROI_timecourse.txt@g" \
                 ${design_template} >> ${fsf_sub}

          echo ${fsf_sub}

        fi
      done
    done
  done

  echo

done


# store all the fsf to run in an array
feat2run=($(find ${fsf_folder} -name *.fsf | sort))

# Create a function that will actually run the feat and export it
do_subj_level_feat() {
  one_fsf=$1
  echo launching feat ${one_fsf}
  feat ${one_fsf}
}

export -f do_subj_level_feat


# Create a function that will actually run the feat
printf '%s\n' "${feat2run[@]}" | xargs -n 1 -P ${numba_cores} -I {} bash -c 'do_subj_level_feat {}'






# EOF

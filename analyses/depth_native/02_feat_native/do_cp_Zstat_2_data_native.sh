#!/bin/bash

gitdir=/data00/layerfMRI/Github_repo/
bd=${gitdir}/layerfMRI/analyses/depth_native/

subject_list=$(</data00/layerfMRI/list_subjects)


for i in ${subject_list[@]}; do

  subdir=sub_`printf %02d ${i}`

  sourcedir_stub=${bd}/02_feat_native/000_subj_level_feat/${subdir}

  targetdir_stub=${bd}/data_native/${subdir}/Zstat/


  for task in 1 2 3 4; do
    for run in 1 2; do

      taskrun=task_${task}_run_${run}

      sourcedir=${sourcedir_stub}_${taskrun}.feat/

      if [ -d ${sourcedir} ]; then

        echo $sourcedir

        # only if the specific taskrun exists, mkdir the targetdir and cp the zstat
        targetdir=${targetdir_stub}/${taskrun}
        mkdir ${targetdir} -p
        cp ${sourcedir}/thresh_zstat*.nii.gz ${targetdir}/

      else
        echo $sourcedir "nun ce sta"
      fi

    done

  done

done



# EOF

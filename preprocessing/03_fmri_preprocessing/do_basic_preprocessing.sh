#!/bin/bash

# run with
# time cat list | xargs -n 1 -P 15 -I {} ./do_basic_preprocessing.sh {}

# list is a text file with one subject number (NON zeropadded) per line

# NB: For subject 01, 04 and 07 there are missing data,
# therefore the scheme of the files is different,
# and for the moment we will not use them


# Error message if no arguments are provided
[ $# -eq 0 ] && { printf "\n Runs motion correction and detrending for a given subject \n"; \
                  printf " Requires template_preproc.fsf to be in the same directory \n\n"
                  printf " Example: ./do_basic_preprocessing.sh 2 \n"; \
                  printf " To run on all subject, use ./launch_do_basic_preprocessing.sh \n\n"; \
                  exit 1; }



# ----------------------  User defined variables ------------------------------

rawdata_dir=/data01/layerfMRI/rawdata_RPI

regdata_dir=/data00/layerfMRI/regdata

fsf_template=${PWD}/template_preproc.fsf

smoothing=0.0  # set as > 0 ONLY for initial ISC! Then set back to 0.0

# ----------------------  End of user defined variables -----------------------


insub=$1
sub=sub_`printf %02d $1`


bd=${rawdata_dir}/${sub}


for nii4d in `find ${bd} -name *run*.nii.gz | sort`; do

  nii4d=`remove_ext ${nii4d}`
  echo working on ${nii4d}


  # make sure you clean previous applications of the script to start anew
  rm -rf ${nii4d}*.feat
  rm -rf ${nii4d}.fsf

  targetdir=`echo ${nii4d} | awk -F "/" '{NF--; print} ' OFS="/"`
  fsf_name=`echo ${nii4d} | awk -F "/" '{print $NF}' | awk -F "." '{print $1}'`.fsf

  dim1=`fslinfo ${nii4d} | grep ^dim1 | awk '{print $2}'`
  dim2=`fslinfo ${nii4d} | grep ^dim2 | awk '{print $2}'`
  dim3=`fslinfo ${nii4d} | grep ^dim3 | awk '{print $2}'`
  dim4=`fslinfo ${nii4d} | grep ^dim4 | awk '{print $2}'`

  totalVoxels=$((dim1*dim2*dim3*dim4))


  # Prepare fsf using the template and sed
  sed -e "s@NIFTI4D@${nii4d}@g"  \
      -e "s@TOTALNUMBAVOXELS@${totalVoxels}@g" \
      -e "s@NUMBATIMEPOINTS@${dim4}@g" \
      -e "s@SMOOTHINGKERNEL@${smoothing}@g" \
         ${fsf_template} > ${targetdir}/${fsf_name}


  # Run feat [sub][taskrun].fsf
  feat ${targetdir}/${fsf_name}


  # Save in regdir
  orig_filename=`echo ${nii4d} | awk -F "/" '{print $NF}'`
  session=`echo ${orig_filename} | awk -F "_" '{print $3,$4}' OFS="_"`
  dest_filename=`echo ${orig_filename} | awk -F "_" '{print $5,$6,$7,$8}' OFS="_"`

  dest_path=${regdata_dir}/${sub}/${session}/func/${dest_filename}_4D.nii.gz

  cp ${nii4d}.feat/filtered_func_data.nii.gz  ${dest_path}

  echo copied ${nii4d}.feat/filtered_func_data.nii.gz
  echo to ${dest_path}
  echo

done










# EOF

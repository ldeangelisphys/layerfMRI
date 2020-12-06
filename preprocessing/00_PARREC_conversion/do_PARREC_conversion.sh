#!/bin/bash

# run with
# time cat list | xargs -n 1 -P 15 -I {} ./do_PARREC_conversion.sh {}

# list is a text file with one subject number (NON zeropadded) per line

# NB: For subject 01, 04 and 07 there are missing data,
# therefore the scheme of the files is different,
# and for the moment we will not use them


# Error message if no arguments are provided
[ $# -eq 0 ] && { clear;
                  printf "\n run with: \n time cat list | xargs -n 1 -P 15 -I {} ./do_PARREC_conversion.sh {} \n\n"; \
                  printf " PARREC files are in /data01/layerfMRI/PARREC/2018_7T_14sub_raw \n\n"; \
                  printf "   ___       \n"
                  printf "  {o,o}     Make sure you decrypted \n"
                  printf "  |)__)     /data01/layerfMRI/PARREC/PARREC.enc \n"
                  printf "  -\"-\"--   before starting the process !! \n\n"
                  exit 1; }


# ------------------------  User defined parameters  --------------------------

# This is the only variable that the script needs
sub=`printf %02d $1`

sourcedir=/data01/layerfMRI/PARREC/2018_7T_14sub_raw
# sourcedir=/data02/ritu/2018_7T_14sub_raw

bd=/data01/layerfMRI/rawdata_RPI/sub_${sub}

# ----------------------  End of user defined parameters  ---------------------





logfile=${bd}/log_sub${sub}


# Print information before running
printf "Using PARREC data from ${sourcedir} \n Converted files will be in ${bd} \n Logfile is ${logfile} \n\n"


# Remove previous data
if [[ -d ${bd} ]]; then
  rm -rf ${bd}
fi


# Create am empty logfile
echo > ${logfile}


# Create the directory tree
for ses in 01 02; do
  mkdir -p ${bd}/ses_${ses}/anat
  mkdir -p ${bd}/ses_${ses}/func
  mkdir -p ${bd}/ses_${ses}/json
done


# Convert with dcm2niix
for ses in 1 2; do

  ses_pad=`printf %02d ${ses}`

  mkdir -p ${bd}/ses_${ses_pad}

  dcm2niix -f sub_${sub}_%p_%s  \
           -o ${bd}/ses_${ses_pad} \
           ${sourcedir}/S${sub}*session${ses}

  mv ${bd}/ses_${ses_pad}/*.json  ${bd}/ses_${ses_pad}/json/

done


# Remove unnecessary files
for ses in 01 02; do
  rm ${bd}/ses_${ses}/*3dT1PlanScan*
  rm ${bd}/ses_${ses}/*fatnav*
  rm ${bd}/ses_${ses}/*B0calibrationbrain*
  rm ${bd}/ses_${ses}/*sagittal*ph.nii
done


# Separate anat from func
for ses in 01 02; do
  mv ${bd}/ses_${ses}/*MP2RAGE* ${bd}/ses_${ses}/anat/
  mv ${bd}/ses_${ses}/*T123* ${bd}/ses_${ses}/anat/
  mv ${bd}/ses_${ses}/*sagittal* ${bd}/ses_${ses}/func/
done


# Move the images for topup in a directory on their own
for ses in 01 02; do
  mkdir ${bd}/ses_${ses}/func/TU
  mv ${bd}/ses_${ses}/func/*TU*.nii ${bd}/ses_${ses}/func/TU
done


# ------------ TO REMOVE IN PRODUCTION ----------------------------------------
# temporary removal, just during development phase

for ses in 01 02; do
  rm -rf ${bd}/ses_${ses}/func/TU
  rm -rf ${bd}/ses_${ses}/json
done
# ------------- REMOVE THE PART ABOVE IN PRODUCTION ---------------------------



# -------------- Remove SENSE from the filename -------------------------------
for ses in 01 02; do

  for filename in `ls ${bd}/ses_${ses}/func/*`; do

      # check that there are such files in this subject
      if [[ "${filename}" == *"SENSE"* ]]; then
        echo ${filename}

        shortname=`echo ${filename} | sed s@SENSE@@g`
        echo ${shortname}

        # do the actual renaming
        mv ${filename} ${shortname}

      fi

  done

done

echo
echo




# ---------------------  Functional of session 01 -----------------------------
ses=01

for task in func_ func2_; do

  # isolate the acquisition number for every task and put it in an array
  arr=($(ls ${bd}/ses_${ses}/func/*${task}* | awk -F_ '{print $NF}' | awk -F. '{print $1}'));
  # echo ${arr[@]};

  # sort the array, because I assume that for every task (func_, func2_ usw)
  # the acquisition with the lower number refers to run1, and the one with
  # the higher number to run2
  # https://unix.stackexchange.com/questions/247655/how-to-create-a-function-that-can-sort-an-array-in-bash
  sortedarr=($(echo ${arr[*]}| tr " " "\n" | sort -n))
  # echo ${sortedarr[@]}

  run=0
  for sortedarr_elem in ${sortedarr[@]}; do

    case ${task} in
      "func_")
          tasknumba=1
          ;;
      "func2_")
          tasknumba=2
          ;;
    esac

    run=$((run+1))
    oldname=${bd}/ses_${ses}/func/*${task}*${sortedarr_elem}.nii
    newname=${bd}/ses_${ses}/func/sub_${sub}_ses_${ses}_task_${tasknumba}_run_${run}.nii
    echo mv ${oldname} >> ${logfile}
    echo "  " ${newname} >> ${logfile}
    echo >> ${logfile}

    # do the actual renaming
    mv ${oldname} ${newname}

  done

done


# ---------------------  Functional of session 02 -----------------------------
ses=02

for task in func3_ func4_; do

  arr=($(ls ${bd}/ses_${ses}/func/*${task}* | awk -F_ '{print $NF}' | awk -F. '{print $1}'));
  # echo ${arr[@]};

  sortedarr=($(echo ${arr[*]}| tr " " "\n" | sort -n))
  # echo ${sortedarr[@]}

  run=0
  for sortedarr_elem in ${sortedarr[@]}; do

    case ${task} in
      "func3_")
          tasknumba=3
          ;;
      "func4_")
          tasknumba=4
          ;;
    esac

    run=$((run+1))
    oldname=${bd}/ses_${ses}/func/*${task}*${sortedarr_elem}.nii
    newname=${bd}/ses_${ses}/func/sub_${sub}_ses_${ses}_task_${tasknumba}_run_${run}.nii
    echo mv ${oldname} >> ${logfile}
    echo "  " ${newname} >> ${logfile}
    echo >> ${logfile}

    # do the actual renaming
    mv ${oldname} ${newname}

  done

done


# --------------------- END of processing FUNCTIONAL scans --------------------






# --------------------- ANATOMICAL SCANS --------------------------------------

# NB: in subj 11 the MP2RAGE full was acquired in the second session, therefore
# we need to first move it to the first session

if [[ ${sub} -eq "11" ]]; then
  mv ${bd}/ses_02/anat/*MP2RAGE*  ${bd}/ses_01/anat/
fi


# --------------------- Rename the anatomical scans ---------------------------
for ses in 01 02; do

  bdanat=${bd}/ses_${ses}/anat

  if [[ ${ses} -eq 01 ]]; then
    mv ${bdanat}/*MP2RAGE*INV1*_??_ph.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_full_inv1ph.nii
    mv ${bdanat}/*MP2RAGE*INV1*_??.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_full_inv1.nii
    mv ${bdanat}/*MP2RAGE*INV2*_??_ph.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_full_inv2ph.nii
    mv ${bdanat}/*MP2RAGE*INV2*_??.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_full_inv2.nii
  fi

  mv ${bdanat}/*T123DEPI*INV1*_??_ph.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_part_inv1ph.nii
  mv ${bdanat}/*T123DEPI*INV1*_??.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_part_inv1.nii
  mv ${bdanat}/*T123DEPI*INV2*_??_ph.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_part_inv2ph.nii
  mv ${bdanat}/*T123DEPI*INV2*_??.nii  ${bdanat}/sub_${sub}_ses_${ses}_acq_part_inv2.nii

done



# ------------------- Reorient everything to RPI ------------------------------

for image in `find ${bd} -name *.nii`; do

  tmp=`remove_ext ${image}`
  fslreorient2std ${tmp} ${tmp}_RPI
  imrm ${tmp}
  immv ${tmp}_RPI ${tmp}

done



# ------------------- Deface the full anatomical using pydeface ---------------
source activate layerfMRI

anatfulldir=${bd}/ses_01/anat
todeface=${anatfulldir}/sub_${sub}_ses_01_acq_full_inv2.nii.gz

echo
echo `conda info | grep "active environment"`
echo
echo Running pydeface on ${todeface}

time pydeface ${todeface} --applyto `ls ${bd}/ses_01/anat/*full*` --force

for defaced_filename in `find ${anatfulldir} -name *defaced*`; do

  filename_no_defaced=`echo ${defaced_filename} | sed s@_defaced@@g`
  mv ${defaced_filename} ${filename_no_defaced}

done






### EOF

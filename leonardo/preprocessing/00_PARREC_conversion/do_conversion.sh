#!/bin/bash


# run with
# time cat list | xargs -n 1 -P 5 -I {} ./do_conversion.sh {}

# sub=02
sub=`printf %02d $1`

sourcedir=/data02/ritu/2018_7T_14sub_raw

bd=/data00/leonardo/layers/rawdata_LIP/sub_${sub}

logfile=/data00/leonardo/layers/rawdata_LIP/sub_${sub}/log_sub${sub}
echo > ${logfile}

# Remove previous build
if [[ -d ${bd} ]]; then
  rm -rf ${bd}
fi

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


# ------------ TO REMOVE IN PRODUCTION ---------------------
# temporary removal, just during development phase

for ses in 01 02; do
  rm -rf ${bd}/ses_${ses}/func/TU
  rm -rf ${bd}/ses_${ses}/json
done
# ------------- REMOVE THE PART ABOVE IN PRODUCTION --------



# -------------- Remove SENSE from the filename --------------
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




# --------------  Functional of session 01 -----------------------------------
ses=01

for task in func_ func2_; do

  arr=($(ls ${bd}/ses_${ses}/func/*${task}* | awk -F_ '{print $NF}' | awk -F. '{print $1}'));
  # echo ${arr[@]};

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


# --------------  Functional of session 02 -----------------------------------
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


# ------------------------------



















### leonardo

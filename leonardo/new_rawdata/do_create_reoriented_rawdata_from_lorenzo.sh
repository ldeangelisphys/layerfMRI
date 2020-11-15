#!/bin/bash

# insub=$1
insub=2

sub=`printf "%02d" ${insub}`

sourcedir='/data00/lorenzo/PROJECTS/layers/rawdata'
targetdir='/data00/leonardo/layers/rawdata_LIP'

for i in `find ${sourcedir}/sub-${sub} -type d`; do

  # echo ${i}
  newdir=`echo ${i} | sed s@${sourcedir}@${targetdir}@g`
  # echo ${newdir}
  mkdir -p ${newdir}

done

echo
echo List files
echo

for infile in `find ${sourcedir}/sub-${sub} -name *.nii.gz`; do


  outfile=`echo ${infile} | sed s@${sourcedir}@${targetdir}@g`

  if [[ ${infile} != *"MNI"* ]]; then

    # echo ${infile}
    # echo ${outfile}

    if [[ ${infile} = *"anat"* ]]; then

      echo ${outfile}

    fi



  fi

done


ciao 

#!/bin/bash

# example: for i in `ls 000_subj_level_feat/*.fsf`; do ./check_fsf.sh ${i}; done

onefsf=$1
echo
echo ---------------- ${onefsf} -------------------
echo

for i in '(outputdir)' '(npts)' '(totalVoxels)' 'feat_files(1)' 'fmri(custom1)' 'fmri(custom2)' ; do
  cat ${onefsf} | grep ${i};
done

echo


# for i in OUTPUTFEATDIR NUMBATIMEPOINTS TOTALNUMBAVOXELS NII4D EVMOTION EVSCRAMBLED; do
#   echo ${i};
#   cat 000_template_design.FSF| grep ${i};
#   echo ;
# done

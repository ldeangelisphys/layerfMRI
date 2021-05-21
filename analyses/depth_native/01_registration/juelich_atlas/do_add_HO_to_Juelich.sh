#!/bin/bash

# This script is to add a region that captures the occipital blob, which lies
# in a region not mapped in the Juelich atlas.
# Such region is covered by the Lateral Occipital Cortex, Inferior division
# in the Harvard-Oxford cortical atlas (region 23, bilateral)

# Since we are using the icbm152_2009 template from nilearn, we first need
# to take the FSL distribution of the HO atlas into this space.
# This can be done by loading the icbm152_2009 and the HO in fsleyes, and then
# use Tools > Resample image, using the icbm as reference. Since it's an atlas,
# remember to use NN interpolation and to uncheck smoothing.
# This has already been done, and the result is
# harvardoxford-cortical_label_all_resampled.nii.gz

# The strategy is to simply isolate the region 23, assign a label numba > than
# the last in the label_juelich.csv, and finally add the region to the
# atlas_juelich_icbm.nii.gz.
# However there are some overlapping JU regions in some part of region 23,
# specifically occupied by V1 and V2.
# So we first need to set to 0 the voxels that will represent region 23. To do this
# we create an inverse mask of region 23, having zeros inside and ones outside
# and the multiply it by the juelich atlas before adding the region 23

HO=harvardoxford-cortical_label_all_resampled.nii.gz
JU=atlas_juelich_icbm_ORIGINAL

# isolate Lateral Occipital Cortex and make a binary mask
fslmaths ${HO} -thr 23 -uthr 23 -bin HO_LOC

# create inverse mask of HO_LOC
fslmaths HO_LOC -sub 1 -mul -1 HO_LOC_inv_mask

# clean that region in the juelich atlas
fslmaths ${JU} -mul HO_LOC_inv_mask ${JU}_clean

# prepare the region to be added to JU, with label 200
fslmaths HO_LOC -mul 200 HO_LOC_label200

# add it to the juelich atlas
fslmaths ${JU}_clean -add HO_LOC_label200  atlas_juelich_icbm.nii.gz

# add the relevant line to the labels_juelich_ORIGINAL.csv
# IMPORTANT: the label is 200-1=199 since in the label files these $%@#@$
# decided to start from zero! So when they are read in the script for depth
# analysis, the first thing is to add 1.
# So the label #199 refers to the region with intensity 200 in the nifti...
cp labels_juelich_ORIGINAL.csv tmp.csv
echo >> tmp.csv
echo 199,GM_HO_Lateral_Occipital_Inferior >> tmp.csv  # Note that it's 199!!!
mv tmp.csv labels_juelich.csv

# housekeeping
rm HO*
rm *clean*

# EOF

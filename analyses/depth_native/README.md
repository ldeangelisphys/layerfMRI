# Cortical depth analysis in native space

This document is also contained at the beginning of `depth_native_analysis_V6_meanZ.Rmd`

---

We are interested in detecting differences in the profile of layer-specific activity during the observation of either scrambled or unscrambled movies representing goal-directed actions.

By _profile of activity_ we mean the activity - estimated using GLM - at different cortical depth (bin). The basic unit of estimation is therefore the activity at a given cortical depth bin.

Estimating this quantity at the group level using a template proved unfeasible at the least, since moderate degrees-of-freedom elastic transformation do not - and should not - perfectly align the morphology of every subject, while aggressive transformation disrupt the single-subject morphology. 

In addition, voxel-level functional localization is already hard to establish for conventional spatial resolution fMRI (2-3mm), and it is therefore practically unfeasible for layer-specific fMRI (~0.6 mm resolution).

This prompted me to devise a different strategy to estimate group-level effects. This strategy is based on two insights:

- carrying out layer-specific estimation in the native space is the best strategy to preserve layer-specific information, which would be lost in interpolations to other-subject spaces, and likely compromised in the transformation to the anatomical scan - as it would require upsampling.
- activity can be quantified at the level of atlas-based cytoarchitectonically defined maps, for which the degree of precision in template-to-subject registration needs not to be extremely precise

In this notebook, I will estimate layer-specific activity for each subject, condition, run, in each of the cytoarchitectonically defined regions in the Juelich atlas. The basic data which needs to be available is therefore, for each subject:

- thresholded Z stat for each contrast and each run in the native space
- cortical depth map for each run registered in the native space
- juelich maps for each run registered in the native space

For each cortical bin in each Juelich region, I will then average the Z values across runs, and finally take this quantity in the group-level analysis. I will leave open the amount of bins to sample the cortical depth with.

The choice of using the thresholded zstat instead of the raw zstat is twofold:

- thresholded zstat are already present only on the map of cortical depth, which is where I want to estimate my statistic
- thresholded zstat have already been corrected for MCP at the subject level

In addition, I need to establish some other criteria for inclusion of the run-level quantities:

- for a given subject, the minimum amount of voxels in each Julich ROI (note that the results have already been corrected with GRF, therefore they can be assimilated to clusters)
- for a given subject, the minimum amount of runs in which a given ROI featured suprathreshold voxels 
- at the group level, minimum amount of subjects having suprathreshold voxels in each ROI

These criteria are indeed quite stringent, since they are based on the single-subject and single-run corrected results. However I believe that this can result in a more robust result. Besides, it would be at least difficult to figure out how to carry out spatial GRF correction here, within each ROI.

Note that the engineering of the method is quite complex, since I have:

- 2 conditions for each run
- 8 runs for each subject
- N Juelich ROIs for each subject/run
- 8 cortical depth maps for each subject (one for each run)
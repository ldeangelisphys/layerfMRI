# Nighres Layering
_Leonardo Cerliani, december 2020_


```
source:       /data01/layerfMRI/rawdata_RPI/
destination:  /data00/layerfMRI/regdata/
```


`do_layering` starts with the raw inversion (and relative phase) acquisitions and
ends up with an estimation of cortical depth and 4 cortical layers - however in the following analysis we will always use only the cortical depth estimation, rather than the layer estimation.

The whole procedure is carried out in [nighres](https://nighres.readthedocs.io/en/latest/) and must be run by
riding on the storm using the layerfMRI conda env.

**NB** The standard procedure is detailed in [Huntenburg 2018](https://academic.oup.com/gigascience/article/7/7/giy082/5049008?login=true), however it has been adapted to yield satisfactory results with our data.

The steps are as follows:

1. Reconstruction of T1w (uni) and T1map from inv1/2 and inv1/2ph :

  - `nighres.intensity.mp2rage_t1_mapping`


2. Intensity-based skull stripping of inv2 and T1map, preceded by an N4antsBiasCorrection due to the extreme inhomogeneities (and artifacts) in our data, and followed by dilation

  - `N4BiasFieldCorrection` (bash; the ANTsPy version goes to seg fault)
  - `nighres.brain.intensity_based_skullstripping`


3. Dura and sulcal ridge estimation and filter stacking

  - `nighres.brain.mp2rage_dura_estimation`
  - `nighres.filtering.filter_ridge_structures`
  - `nighres.brain.filter_stacking`


4. MGDM segmentation using the default atlas

  - `nighres.brain.mgdm_segmentation`


5. LH region extraction

  - `nighres.brain.extract_brain_region`


6. Cruise cortical extraction

  - `nighres.cortex.cruise_cortex_extraction`


7. Volumetric layering

  - `nighres.laminar.volumetric_layering`

QC images for skull stripping, cortical ribbon and cortical depth are produced in the QC folder


---

<details>
<summary> Example output: </summary>
<p>

```bash

/data00/regdata/layerfMRI/
│
sub_02/ses_01/anat/layering/
│
├── 000_last_completed_stage.txt
├── LH_cortex_xlvl-lcrbg.nii.gz
├── LH_cortex_xlvl-lcrgm.nii.gz
├── LH_cortex_xlvl-lcrwm.nii.gz
├── LH_cortex_xmask-lcrbg.nii.gz
├── LH_cortex_xmask-lcrgm.nii.gz
├── LH_cortex_xmask-lcrwm.nii.gz
├── LH_cortex_xproba-lcrbg.nii.gz
├── LH_cortex_xproba-lcrgm.nii.gz
├── LH_cortex_xproba-lcrwm.nii.gz
│
├── LH_cruise_cruise-avg.nii.gz
├── LH_cruise_cruise-cgb.nii.gz
├── LH_cruise_cruise-cortex.nii.gz
├── LH_cruise_cruise-gwb.nii.gz
├── LH_cruise_cruise-pcsf.nii.gz
├── LH_cruise_cruise-pgm.nii.gz
├── LH_cruise_cruise-pwm.nii.gz
├── LH_cruise_cruise-thick.nii.gz
│
├── LH_layering_layering-boundaries.nii.gz
├── LH_layering_layering-depth.nii.gz
├── LH_layering_layering-depth_MNI.nii.gz
├── LH_layering_layering-depth_MNIspace.nii.gz
├── LH_layering_layering-layers.nii.gz
├── LH_layering_layering-layers_MNIspace.nii.gz
│
├── dura_dura-proba.nii.gz
├── filter_stack_bfs-img.nii.gz
├── istrip_istrip-extra.nii.gz
├── istrip_istrip-main.nii.gz
├── istrip_istrip-mask.nii.gz
├── istrip_istrip-proba.nii.gz
├── istrip_istrip-t1w.nii.gz
│
├── mgdm_mgdm-dist.nii.gz
├── mgdm_mgdm-lbls.nii.gz
├── mgdm_mgdm-mems.nii.gz
├── mgdm_mgdm-seg.nii.gz
│
├── recon_qt1map-r1.nii.gz
├── recon_qt1map-t1.nii.gz
├── recon_qt1map-uni.nii.gz
└── ridge_rdg-img.nii.gz
```

</p>
</details>  

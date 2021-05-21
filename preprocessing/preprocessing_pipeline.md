# Preprocessing pipeline

The following series of scripts takes as input a set of PAR/REC files, convert them to NIFTI images and prepare all the necessary data for cortical-depth dependent fmri analysis.

There are currently two directories (dirs) on our server (storm) which contain all the data:

- `data01/layerfmri` : contains the raw `PARREC` (encrypted) and a directory `rawdata_RPI` which contains intermediate steps of the preprocessing. These data are not necessary for the analysis and therefore are stored on a slow-access disk (`data01`)

- `data00/layerfmri/regdata` : contains only preprocessed data which is necessary for the analysis, and therefore is placed in this fast-access disk (`data00`). This is also the location of the quality control images produced after most of the preprocessing steps.

If you want to carry out the preprocessing/analysis after moving the data to another location, the best would be to [clone the entire repository](https://github.com/ldeangelisphys/layerfMRI), and manually modify the location of these two dirs manually, which is generally found at the beginning of each script. In the following, replace the original directory names with the new locations to be able to follow the instructions and run the scripts successfully. Also, don't forget to recreate the `layerfMRI` conda environment and install the necessary dependencies as explained in [the main page of the repo](https://github.com/ldeangelisphys/layerfMRI).

The scripts are already placed in dirs whose first two numbers indicate the order in which they should launched. Below is a comprehensive set of instructions which complement the README.md file in each step.

## 00_PARREC_conversion

```
source:       /data01/layerfMRI/PARREC/2018_7T_14sub_raw
destination:  /data01/layerfMRI/rawdata_RPI/sub_${sub}
```

The PARREC have been encrypted with openssl since from them it is possible to reconstruct the original images, and therefore there is - at least in theory - the possibility to identify the participants from the anatomical MRI image.

Therefore before launching this script, you should make sure that the directory with the PARREC has been decrypted. All the instructions for this are in
`/data01/layerfMRI/PARREC/README_FIRST.txt`. The pw to decrypt is of course not included and should be asked to me.


`do_PARREC_conversion.sh` : carries out the conversion from PAR/REC format to compressed nifti (nii.gz) and reorient the images to RPI

`list` : is a text file with the id of the participants to process

The `do_PARREC_conversion.sh` script is generally not called directly, but rather in parallel for all subjects using:

```
time cat list | xargs -n 1 -P 15 -I {} ./do_PARREC_conversion.sh {}
```
It's recommendable to run this command inside `screen`. __ETA is about 1hr__.

If instead you want to convert a single participant's PAR/REC files, then pass the _non zeropadded_ id to the script, e.g.:

```
./do_PARREC_conversion.sh 2
```

__IMPORTANT:__ The script will erase any previous conversion! (i.e. destination folder)



<details>
<summary>Example output:</summary>
<p>

```bash
/data01/layerfMRI/rawdata_RPI/
│
sub_02
├── log_sub02
├── ses_01
│   ├── anat
│   │   ├── sub_02_ses_01_acq_full_inv1.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv1ph.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv2.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv2ph.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv1.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv1ph.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv2.nii.gz
│   │   └── sub_02_ses_01_acq_part_inv2ph.nii.gz
│   └── func
│       ├── sub_02_ses_01_task_1_run_1.nii.gz
│       ├── sub_02_ses_01_task_1_run_2.nii.gz
│       ├── sub_02_ses_01_task_2_run_1.nii.gz
│       └── sub_02_ses_01_task_2_run_2.nii.gz
└── ses_02
    ├── anat
    │   ├── sub_02_ses_02_acq_part_inv1.nii.gz
    │   ├── sub_02_ses_02_acq_part_inv1ph.nii.gz
    │   ├── sub_02_ses_02_acq_part_inv2.nii.gz
    │   └── sub_02_ses_02_acq_part_inv2ph.nii.gz
    └── func
        ├── sub_02_ses_02_task_3_run_1.nii.gz
        ├── sub_02_ses_02_task_3_run_2.nii.gz
        ├── sub_02_ses_02_task_4_run_1.nii.gz
        └── sub_02_ses_02_task_4_run_2.nii.gz
```

</p>
</details>  


## 01_MP2RAGE_reconstruction

```
source:       /data01/layerfMRI/rawdata_RPI/
destination:  /data01/layerfMRI/rawdata_RPI/
```

The process is launched with `./launch_MP2RAGE_reconstruction.sh`, which contains also a list of SUB_ID as a bash array.

The launcher calls parallel instances of `do_MP2RAGE_reconstruction.py` to process all participants.

Calling `python do_MP2RAGE_reconstruction.py` by itself will provide usage information.

This script uses `nighres.intensity.mp2rage_t1_mapping`.

**ETA is about 1 minute**

<details>
<summary>Example output:</summary>
<p>


<pre>

/data01/layerfMRI/rawdata_RPI
|
sub_02
├── log_sub02
├── ses_01
│   └── anat
│       ├── <b>sub_02_ses_01_acq_full_T1map.nii.gz </b>
│       └── <b>sub_02_ses_01_acq_full_T1w.nii.gz </b>
└── ses_02
    └── anat
        ├── <b>sub_02_ses_02_acq_part_T1map.nii.gz</b>
        └── <b>sub_02_ses_02_acq_part_T1w.nii.gz</b>

</pre>

</p>
</details>  


## 02_skull_stripping

```
source:       /data01/layerfMRI/rawdata_RPI/
destination:  /data00/layerfMRI/regdata/
```

`do_skullstrip.py` : carries out the entire procedure from the raw images for one subject. Type `python do_skullstrip.py -h` to have information about the parameters

`launch_do_skullstrip.sh` : launches N processes of `do_skullstrip.py` in parallel to process all subjects. __ETA is about 6'__

At the end, one QC folder will be produced in the root of each participant, containing an HTML file with the overlay of the mask on top of the either anatomy or mean functional.


<details>
<summary>Example output:</summary>
<p>

```bash

/data00/layerfMRI/regdata/
│
sub_02
├── QC
│   └── skullstrip
│       ├── images
│       │   ├── full_anat_mask.png
│       │   ├── sub_02_ses_01_T123.png
│       │   ├── sub_02_ses_01_task_1_run_1.png
│       │   ├── sub_02_ses_01_task_1_run_2.png
│       │   ├── sub_02_ses_01_task_2_run_1.png
│       │   ├── sub_02_ses_01_task_2_run_2.png
│       │   ├── sub_02_ses_02_T123.png
│       │   ├── sub_02_ses_02_task_3_run_1.png
│       │   ├── sub_02_ses_02_task_3_run_2.png
│       │   ├── sub_02_ses_02_task_4_run_1.png
│       │   └── sub_02_ses_02_task_4_run_2.png
│       ├── skullstrip.html
│       └── skullstrip.md
├── ses_01
│   └── anat
│       ├── full_T1w.nii.gz
│       ├── full_T1w_brain.nii.gz
│       ├── full_T1w_brain_mask.nii.gz
│       ├── part_T1w.nii.gz
│       ├── part_T1w_brain.nii.gz
│       └── part_T1w_brain_mask.nii.gz
└── ses_02
    └── anat
        ├── part_T1w.nii.gz
        ├── part_T1w_brain.nii.gz
        └── part_T1w_brain_mask.nii.gz
```

</p>
</details>  


## 03_fmri_preprocessing

```
source:       /data01/layerfMRI/rawdata_RPI/
destination:  /data00/layerfMRI/regdata/
```

`do_basic_processing.sh` : carries out realignment and detrending of the raw images for one subject. Run it alone to have information about the parameters

`launch_do_basic_processing.sh` : launches N processes of `do_basic_processing.sh` in parallel to process all subjects. __ETA is about 2.5 hrs__

__Note__: the raw data is in `/data01/layerfMRI/rawdata_RPI`, where the report html with estimated movement parameters will be found, e.g. `sub_02_ses_01_task_1_run_1.feat/report.html`

The preprocessed 4D is instead in `/data00/layerfMRI/regdata`

<details>
<summary>Example output:</summary>
<p>

```bash

/data00/layerfMRI/regdata/
│
sub_02
├── ses_01
│   └── func
│       ├── task_1_run_1_4D.nii.gz
│       ├── task_1_run_2_4D.nii.gz
│       ├── task_2_run_1_4D.nii.gz
│       └── task_2_run_2_4D.nii.gz
└── ses_02
    └── func
        ├── task_3_run_1_4D.nii.gz
        ├── task_3_run_2_4D.nii.gz
        ├── task_4_run_1_4D.nii.gz
        └── task_4_run_2_4D.nii.gz
```

</p>
</details>


## 04_registration


```
source:       /data00/layerfMRI/regdata/
destination:  /data00/layerfMRI/regdata/
```

### Estimate transformations
`do_estimate_transformation.py` : carries out estimation of the alignment between each `fmri[session][taskrun]` and the MNI 1mm, in the following order:

```
MNI <-- full anat <-- part anat <-- fmri
```

**NB: everything related to registration with ANTs should be read from right to left,** e.g. `MNI_fmri` indicates a transformation `fmri --> MNI`

`launch_do_estimate_transformation.sh` : launches N processes of `do_estimate_transformation.py` in parallel to process all subjects. The number of threads used by ANTs can be chosen as an argument of `do_estimate_transformation.py`

The single-stage as well as composite transformations are saved in `/data00/layerfMRI/regdata/sub_[SUB_ID]/reg`

Overlays of registration results are produced in the `/registration.html` file of each subject's QC directory

__ETA is about 30' with 5 threads per subject__


### Apply `fmri <-- MNI` transformations
`do_apply_transformation.py` : applies the MNI_fmri transformation estimated in the script above
`launch_do_apply_transformation.sh` : launches N processes of `do_apply_transformation.py` in parallel to process all subjects, with 5 threads per subject.

__ETA is about 1.5 hours__ since due to memory limitation I can only process at max 4 participants at the time.


The data is taken from and stored in `/data00/layerfMRI/regdata/`. Specifically, the following two composite transformations are stored in the `/reg` subdir of each participant.


<details>
<summary> Example output: </summary>
<p>

```bash

/data00/regdata/layerfMRI/
│
sub_02
├── QC
│   └── registration
│       ├── images
│       │   ├── fig001_sub_02_MNI_full.png
│       │   ├── fig002_sub_02_full_part_ses_01.png
│       │   ├── fig002_sub_02_full_part_ses_02.png
│       │   ├── fig003_sub_02_part_fmri_task_1_run_1.png
│       │   ├── fig003_sub_02_part_fmri_task_1_run_2.png
│       │   ├── fig003_sub_02_part_fmri_task_2_run_1.png
│       │   ├── fig003_sub_02_part_fmri_task_2_run_2.png
│       │   ├── fig003_sub_02_part_fmri_task_3_run_1.png
│       │   ├── fig003_sub_02_part_fmri_task_3_run_2.png
│       │   ├── fig003_sub_02_part_fmri_task_4_run_1.png
│       │   └── fig003_sub_02_part_fmri_task_4_run_2.png
│       ├── registration.html
│       └── registration.md
├── reg
│   ├── MNI_fmri_ses_01_task_1_run_1_comptx.nii.gz
│   ├── MNI_fmri_ses_01_task_1_run_2_comptx.nii.gz
│   ├── MNI_fmri_ses_01_task_2_run_1_comptx.nii.gz
│   ├── MNI_fmri_ses_01_task_2_run_2_comptx.nii.gz
│   ├── MNI_fmri_ses_02_task_3_run_1_comptx.nii.gz
│   ├── MNI_fmri_ses_02_task_3_run_2_comptx.nii.gz
│   ├── MNI_fmri_ses_02_task_4_run_1_comptx.nii.gz
│   ├── MNI_fmri_ses_02_task_4_run_2_comptx.nii.gz
│   ├── fmri_MNI_ses_01_task_1_run_1_comptx.nii.gz
│   ├── fmri_MNI_ses_01_task_1_run_2_comptx.nii.gz
│   ├── fmri_MNI_ses_01_task_2_run_1_comptx.nii.gz
│   ├── fmri_MNI_ses_01_task_2_run_2_comptx.nii.gz
│   ├── fmri_MNI_ses_02_task_3_run_1_comptx.nii.gz
│   ├── fmri_MNI_ses_02_task_3_run_2_comptx.nii.gz
│   ├── fmri_MNI_ses_02_task_4_run_1_comptx.nii.gz
│   └── fmri_MNI_ses_02_task_4_run_2_comptx.nii.gz
├── ses_01
│   └── func
│       ├── task_1_run_1_4D_MNI.nii.gz
│       ├── task_1_run_2_4D_MNI.nii.gz
│       ├── task_2_run_1_4D_MNI.nii.gz
│       └── task_2_run_2_4D_MNI.nii.gz
└── ses_02
    └── func
        ├── task_3_run_1_4D_MNI.nii.gz
        ├── task_3_run_2_4D_MNI.nii.gz
        ├── task_4_run_1_4D_MNI.nii.gz
        └── task_4_run_2_4D_MNI.nii.gz
```

</p>
</details>  



## 05_layering

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
















---
`EOF`

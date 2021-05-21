# ANTsPy Registration
_Leonardo Cerliani, november 2020_

```
source:       /data00/layerfMRI/regdata/
destination:  /data00/layerfMRI/regdata/
```

## 01. Estimate transformations
`do_estimate_transformation.py` : carries out estimation of the alignment between each `fmri[session][taskrun]` and the MNI 1mm, in the following order:

```
MNI <-- full anat <-- part anat <-- fmri
```

**NB: everything related to registration with ANTs should be read from right to left,** e.g. `MNI_fmri` indicates a transformation `fmri --> MNI`

`launch_do_estimate_transformation.sh` : launches N processes of `do_estimate_transformation.py` in parallel to process all subjects. The number of threads used by ANTs can be chosen as an argument of `do_estimate_transformation.py`

The single-stage as well as composite transformations are saved in `/data00/layerfMRI/regdata/sub_[SUB_ID]/reg`

Overlays of registration results are produced in the `/registration.html` file of each subject's QC directory

__ETA is about 30' with 5 threads per subject__


## 02. Apply `fmri <-- MNI` transformations
`do_apply_transformation.py` : applies the MNI_fmri transformation estimated in the script above
`launch_do_apply_transformation.sh` : launches N processes of `do_apply_transformation.py` in parallel to process all subjects, with 5 threads per subject.

__ETA is about 1.5 hours__ since due to memory limitation I can only process at max 4 participants at the time.


The data is taken from and stored in `/data00/layerfMRI/regdata/`. Specifically, the following two composite transformations are stored in the `/reg` subdir of each participant.

---

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

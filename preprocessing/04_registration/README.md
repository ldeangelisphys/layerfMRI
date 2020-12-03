# ANTsPy Registration
_Leonardo Cerliani, november 2020_

## 01. Estimate transformations
`do_estimate_transformation.py` : carries out estimation of the alignment between each `fmri[session][taskrun]` and the MNI 1mm, in the following order:

```
fmri <-- part_anat <-- full_anat <-- MNI
```

`launch_do_estimate_transformation.sh` : launches N processes of `do_estimate_transformation.py` in parallel to process all subjects. The number of threads used by ANTs can be chosen as an argument of `do_estimate_transformation.py`

Overlays of registration results are produced in the `/registration.html` file of each subject's QC directory.

__ETA is about 15' with 5 threads per subject__

---

## 02. Apply `fmri <-- MNI` transformations
`do_apply_transformation.py` : applies the MNI_fmri transformation estimated in the script above
`launch_do_apply_transformation.sh` : launches N processes of `do_apply_transformation.py` in parallel to process all subjects, with 5 threads per subject.

__ETA is about 3 hours__ because due to memory limitation I can only process five participants at the time.


The data is taken from and stored in `/data00/layerfMRI/regdata/`. Specifically, the following two composite transformations are stored in the `/reg` subdir of each participant.

---

<details>
<summary> Example output: </summary>
<p>

```bash

regdata/sub_02
├── QC
│   ├── registration
│   │   ├── images
│   │   │   ├── fig001_sub_02_MNI_full.png
│   │   │   ├── fig002_sub_02_full_part_ses_01.png
│   │   │   ├── fig002_sub_02_full_part_ses_02.png
│   │   │   ├── fig003_sub_02_part_fmri_task_1_run_1.png
│   │   │   ├── fig003_sub_02_part_fmri_task_1_run_2.png
│   │   │   ├── fig003_sub_02_part_fmri_task_2_run_1.png
│   │   │   ├── fig003_sub_02_part_fmri_task_2_run_2.png
│   │   │   ├── fig003_sub_02_part_fmri_task_3_run_1.png
│   │   │   ├── fig003_sub_02_part_fmri_task_3_run_2.png
│   │   │   ├── fig003_sub_02_part_fmri_task_4_run_1.png
│   │   │   └── fig003_sub_02_part_fmri_task_4_run_2.png
│   │   ├── registration.html
│   │   └── registration.md
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
│       ├── task_2_run_2_4D_MNI.nii.gz
└── ses_02
    └── func
        ├── task_3_run_1_4D_MNI.nii.gz
        ├── task_3_run_2_4D_MNI.nii.gz
        ├── task_4_run_1_4D_MNI.nii.gz
        ├── task_4_run_2_4D_MNI.nii.gz
```

</p>
</details>  



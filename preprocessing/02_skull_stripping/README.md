# Skull stripping
_Leonardo Cerliani, november 2020_

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

# T1w and T1map estimattion from MP2RAGE scans

The process is launched with `./launch_MP2RAGE_reconstruction.sh`.

This calls parallel instances of `do_MP2RAGE_reconstruction.py` to process all participants.
Calling `python do_MP2RAGE_reconstruction.py` by itself will provide usage information.

`do_MP2RAGE_reconstruction.py` has two defaults for the disk location and the rawdata folder. 
If you want to use your own parameters for the parallel processing across all subjects 
you need to edit `launch_MP2RAGE_reconstruction.sh`

Example output:
```
sub_02
├── log_sub02
├── ses_01
│   ├── anat
│   │   ├── sub_02_ses_01_acq_full_inv1.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv1ph.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv2.nii.gz
│   │   ├── sub_02_ses_01_acq_full_inv2ph.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv1.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv1ph.nii.gz
│   │   ├── sub_02_ses_01_acq_part_inv2.nii.gz
│   │   └── sub_02_ses_01_acq_part_inv2ph.nii.gz
│   └── func
│       ├── sub_02_ses_01_task_1_run_1.nii.gz
│       ├── sub_02_ses_01_task_1_run_2.nii.gz
│       ├── sub_02_ses_01_task_2_run_1.nii.gz
│       └── sub_02_ses_01_task_2_run_2.nii.gz
└── ses_02
    ├── anat
    │   ├── sub_02_ses_02_acq_part_inv1.nii.gz
    │   ├── sub_02_ses_02_acq_part_inv1ph.nii.gz
    │   ├── sub_02_ses_02_acq_part_inv2.nii.gz
    │   └── sub_02_ses_02_acq_part_inv2ph.nii.gz
    └── func
        ├── sub_02_ses_02_task_3_run_1.nii.gz
        ├── sub_02_ses_02_task_3_run_2.nii.gz
        ├── sub_02_ses_02_task_4_run_1.nii.gz
        └── sub_02_ses_02_task_4_run_2.nii.gz
```

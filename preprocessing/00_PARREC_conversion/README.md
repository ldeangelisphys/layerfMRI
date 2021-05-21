# PAR/REC conversion and reorienting to RPI
_Leonardo Cerliani, november 2020_

```
source:       /data01/layerfMRI/PARREC/2018_7T_14sub_raw
destination:  /data01/layerfMRI/rawdata_RPI/sub_${sub}
```

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

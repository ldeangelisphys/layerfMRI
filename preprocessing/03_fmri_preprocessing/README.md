# Basic fMRI preprocessing (realignment, detrending)
_Leonardo Cerliani, december 2020_

```
source:       /data01/layerfMRI/rawdata_RPI/
destination:  /data00/layerfMRI/regdata/
```

`do_basic_processing.sh` : carries out realignment and detrending of the raw images for one subject. Run it alone to have information about the parameters

`launch_do_basic_processing.sh` : launches N processes of `do_basic_processing.sh` in parallel to process all subjects. __ETA is about 2.5 hrs__

__Note__: the raw data is in `/data01/layerfMRI/rawdata_RPI`, where the report html with estimated movement parameters will be found, e.g. `sub_02_ses_01_task_1_run_1.feat/report.html`

The preprocessed 4D is instead in `/data00/layerfMRI/regdata`

**Important note**
After this preprocessing was carried out, we noticed problems with the data
of two participants - in addition to the originally excluded subjects 1,4,7 -
which led to their exclusion from further analysis:

- **subject 8** was excluded due to high motion and incomplete data acquisition
- **subject 13** was excluded due to inconsistency between fMRI and log files


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

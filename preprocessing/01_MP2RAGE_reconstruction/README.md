# T1w and T1map estimation from MP2RAGE scans
_Leonardo Cerliani, november 2020_

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

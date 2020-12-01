# ANTsPy Registration
_Leonardo Cerliani, november 2020_

`do_estimate_transformation.py` : carries out estimation of the alignment between each `fmri[session][taskrun]` and the MNI 1mm, in the following order:

```
fmri <-- part_anat <-- full_anat <-- MNI
```

`launch_do_estimate_transformation.sh` : launches N processes of `do_estimate_transformation.py` in parallel to process all subjects. The number of threads used by ANTs can be chosen as an argument of `do_estimate_transformation.py`

__ETA is about 15' with 5 threads per subject__


`do_apply_transformation.py` : applies the MNI_fmri transformation estimated in the script above
`launch_do_apply_transformation.sh` : launches N processes of `do_apply_transformation.py` in parallel to process all subjects, with 5 threads per subject.

__ETA is about 6 hours__ because due to memory limitation I can only process two participants at the time.


The data is taken from and stored in `/data00/leonardolayers/regdata/`. Specifically, the following two composite transformations are stored in the `/reg` subdir of each participant.

Overlays of registration results are produced in the `/registration.html` file of each subject's QC directory.

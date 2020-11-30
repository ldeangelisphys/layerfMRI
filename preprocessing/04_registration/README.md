# ANTsPy Registration
_Leonardo Cerliani, november 2020_

`do_registration.py` : carries out estimation of the alignment between each `fmri[session][taskrun]` and the MNI 1mm, in the following order:

```
fmri <-- part_anat <-- full_anat <-- MNI
```

`launch_do_registration.sh` : launches N processes of `do_registration.py` in parallel to process all subjects. The number of threads used by ANTs can be chosen as an argument of `do_registration.py`

__ETA is about 15' with 5 threads per subject__


The data is taken from and stored in `/data00/leonardolayers/regdata/`. Specifically, the following two composite transformations are stored in the `/reg` subdir of each participant.

Overlays of registration results are produced in the `/registration.html` file of each subject's QC directory.

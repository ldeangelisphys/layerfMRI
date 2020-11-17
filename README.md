
# SBL layer fMRI

This is our official repository for processing the data for layer fMRI analysis acquired at the Spinoza Center in Amstedam.

Each step of the process (processing only so far) is stored within a folder that contains both the notebook - where the operations where tested - and the script to launch the preprocessing/analysis steps separately one from the other.

Each folder name is preceded by a number indicating which other steps should be carried out in advance.

For instance at the moment there are only the initial skull stripping methods:

```
|____preprocessing

| |____01_skull_stripping
| | |____do_adjust_skull_strip_subj8.sh
| | |____do_skullstrip.py
| | |____skull_stripping.ipynb
| | |____README.md
| | |____launch_do_skullstrip.sh
| |
| |____02_fmri_preprocessing
| | |____tobedone
| |
| |____03_registration
| | |____tobedone
```

There are also personal folders where each of us can store notebook/scripts or whatever else should be shared.


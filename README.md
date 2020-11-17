
# SBL layer fMRI

This is our official repository for processing the data for layer fMRI analysis acquired at the Spinoza Center in Amstedam in 2018.

Each step of the process (preprocessing only so far) is stored within a folder that contains the script(s) to launch each preprocessing/analysis steps separately one from the other.

Each folder name is preceded by a number indicating which the order in which the scripts should be run.

The `layerfMRI` conda environment can be recreated locally with

```
conda env create -f layerfMRI_conda_env.yml
```
or updated with 
```
conda env update --prefix ./env --file layerfMRI_conda_env.yml  --prune
```

There are also personal folders where each of us can store notebook/scripts or whatever else should be shared.

Dependencies:
- [nighres](https://nighres.readthedocs.io/en/latest/)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki)
- [AFNI](https://afni.nimh.nih.gov/)
- [pandoc](https://pandoc.org/installing.html)
- [ANTsPy](https://github.com/ANTsX/ANTsPy) ([documentation](https://antspyx.readthedocs.io/en/latest/))

![image](https://cdn.pixabay.com/photo/2015/11/23/13/52/stones-1058365_960_720.jpg)

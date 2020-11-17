
# SBL layer fMRI

This is our official repository for processing the data for layer fMRI analysis acquired at the Spinoza Center in Amstedam in 2018.

Each step of the process (preprocessing only so far) is stored within a folder that contains the script to launch the preprocessing/analysis steps separately one from the other.

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


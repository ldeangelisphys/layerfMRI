
# SBL layer fMRI

This is the official repository of the R/Python/bash scripts used to process the anatomical and high-resolution 7T layer fMRI data on action prediction, acquired at the Spinoza Center in Amstedam in 2018.

These analyses converged into the following manuscript published on Cortex: [Predictive coding during action observation - a depth-resolved intersubject functional correlation study at 7T.](https://www.sciencedirect.com/science/article/pii/S0010945222000016){target="_blank"}


Each step of the process is stored within a folder that contains the script(s) to launch each preprocessing/analysis steps separately one from the other.

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

This work was funded by the [BIAL foundation](https://www.bial.com/com/bial-foundation/) grant 255/16 and the [European Commission ERC](https://erc.europa.eu/) grant VicariousBrain (ERC-StG 312511)

<details>
<summary>Dependencies</summary>

- [ANTsPy](https://github.com/ANTsX/ANTsPy) ([documentation](https://antspyx.readthedocs.io/en/latest/))
- [dcm2niix](https://github.com/rordenlab/dcm2niix/releases)
- [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki)
- [nighres](https://nighres.readthedocs.io/en/latest/)
- [pandoc](https://pandoc.org/installing.html)
- [pydeface](https://github.com/poldracklab/pydeface)

</details>



![image](https://cdn.pixabay.com/photo/2015/11/23/13/52/stones-1058365_960_720.jpg)

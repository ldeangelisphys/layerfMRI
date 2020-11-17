# PAR/REC conversion and reorienting to RPI

`do_PARREC_conversion.sh` : carries out the conversion from PAR/REC format to compressed nifti (nii.gz) and reorient the images to RPI
`list` : is a text file with the id of the participants to process

The `do_PARREC_conversion.sh` script should _not_ be called alone, but rather in parallel for all subjects:

```
time cat list | xargs -n 1 -P 15 -I {} ./do_PARREC_conversion.sh {}
```
It's recommendable to run this command inside `screen`

If instead you want to convert a single participant's PAR/REC files, then pass the _non zeropadded_ id to the script, e.g.:

```
./do_PARREC_conversion.sh 2
```

__IMPORTANT:__ The script will erase any previous conversion! (i.e. destination folder)

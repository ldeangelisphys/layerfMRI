# Skull stripping
_Leonardo Cerliani, november 2020_


`do_skullstrip.py` : carries out the entire procedure from the raw images for one subject. Type `python do_skullstrip.py -h` to have information about the parameters

`launch_do_skullstrip.sh` : launches N processes of `do_skullstrip.py` in parallel to process all subjects. __ETA is about 6'__

__Important Note__ : the rawdata is stored in
`/data00/leonardolayers/rawdata_RPI/`

At the end, one QC folder will be produced in the root of each participant, containing an HTML file with the overlay of the mask on top of the either anatomy or mean functional.

---

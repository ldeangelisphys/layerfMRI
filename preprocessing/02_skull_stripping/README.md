# Skull stripping

__Main scripts__

`do_skullstrip.py` : carries out the entire procedure from the raw images for one subject. Type `python do_skullstrip.py -h` to have information about the parameters

`launch_do_skullstrip.sh` : launches N processes of `do_skullstrip.py` in parallel to process all subjects. __ETA is about 5'__

__Important Note__ : the rawdata is stored in
`/data00/leonardolayers/rawdata_RPI/`

At the end, one QC folder will be produced in the root of each participant, containing an HTML file with the overlay of the mask on top of the either anatomy or mean functional.

---

__Other scripts__

`do_adjust_skull_strip_subj8.sh` : this should be run _after_ the scripts above, and corrects for the results in subj 8, which are suboptimal with the implemented routine

`skull_stripping.ipynb` : the colab notebook used to write and test the functions used for skull stripping in `do_skullstrip.py`

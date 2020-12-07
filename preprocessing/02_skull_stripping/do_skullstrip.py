import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Carry out skull stripping of full anat, part anat, mean func',
                epilog='Example: python do_skullstrip.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba", type=int)

args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)

# -------------- User defined parameters ----------------------

sub=args.sub

finroot = '/data01/layerfMRI/rawdata_RPI/'
foutroot = '/data00/layerfMRI/'

# Define reg_dir for this subject, and create it if not there
reg_dir = foutroot + 'regdata/sub_{:02d}/'.format(sub)
if not os.path.isdir(reg_dir):
        os.makedirs(reg_dir)

# Limit the numba of threads per subject
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = '5'

# -------------- End of User defined parameters ---------------



print("Processing subject " + str(sub))
print("rawdata source is " + finroot + 'sub-{:02d}/'.format(sub))
print("target directory is " + foutroot + 'regdata/sub-{:02d}/'.format(sub))
print(" ")

# sys.exit(1)


# Load libraries
import nibabel as nib
import numpy as np
import json

import nighres
import ants
from nilearn.image import mean_img


# Only in notebook
# !pip install ipython-autotime
# %load_ext autotime

# -------------------- Functions ---------------------------------------

# Function to fetch the data and create the dictionary
def fetch_data(in_dir,reg_dir,sub,ses):

    # Fetch anatomical
    anat = {}
    for a in ['full','part']:
        anat[a] = {}
        for ses in [1,2]:
            anat[a][ses] = {}
            for n in ['inv1','inv1ph','inv2','inv2ph','T1w','T1map']:
                entry = finroot + 'sub_{:02d}/ses_{:02d}/anat/sub_{:02d}_ses_{:02d}_acq_{}_{}.nii.gz'.format(sub,ses,sub,ses,a,n)
                if os.path.isfile(entry):
                    anat[a][ses][n] = entry

    # There is only one session for full, so I delete the level associated to the ses
    if len(anat['full'][1]) > 0:
        anat['full'] = anat['full'][1]
    elif len(anat['full'][2]) > 0 :
        anat['full'] = anat['full'][2]


    # Fetch functional
    func = {}
    for ses in [1,2]:
        func[ses] = {}
        func_fld = finroot + 'sub_{:02d}/ses_{:02d}/func/'.format(sub,ses)
        func_files = [f for f in os.listdir(func_fld)]

        for f in func_files:
            task = f.split('task_')[1].split('_')[0]
            run  = f.split('run_')[1].split('_')[0].replace('.nii.gz','')
            func[ses]['task_{}_run_{}'.format(task,run)] = func_fld + f

    return anat,func


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))




# Produce an image of the T1 with the mask overlaid on top
def produce_png_T1w(sub,bg_img,mask):
  ants.plot(
      bg_img, overlay=mask, overlay_alpha=0.3,
      overlay_cmap='autumn', axis=0, nslices=32, ncol=8,
      title = 'mask full anat sub {:02d}'.format(sub),
      filename=reg_dir + 'QC/skullstrip/images/full_anat_mask.png'.format(mask),
      dpi=72
  )



# Produce an image of the functional mask for QC
def produce_png_func(sub,ses,taskrun,reg_dir,bg_img,mask):
  ants.plot(
      bg_img, overlay=mask, overlay_alpha=0.4,
      overlay_cmap='autumn', axis=0, nslices=32, ncol=8,
      slices=(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9),
      title = 'mask func sub_{:02d}_ses_{:02d}   {}'.format(sub,ses,taskrun),
      filename=reg_dir + 'QC/skullstrip/images/sub_{:02d}_ses_{:02d}_{}.png'.format(sub,ses,taskrun),
      dpi=72
  )



# Produce an image of the T123 mask for QC
def produce_png_T123(sub,ses,reg_dir,bg_img,mask):
  ants.plot(
      bg_img, overlay=mask, overlay_alpha=0.4,
      overlay_cmap='autumn', axis=0, nslices=32, ncol=8,
      slices=(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9),
      title = 'mask T123 sub_{:02d}_ses_{:02d}_{}'.format(sub,ses,'T123'),
      filename=reg_dir + 'QC/skullstrip/images/sub_{:02d}_ses_{:02d}_{}.png'.format(sub,ses,'T123'),
      dpi=72
  )









# ------------------- Full Anatomical skull stripping -------------------------
def skullstrip_anatomical(sub,anat,reg_dir):

  # inv2 bias correction
  full_inv2 = ants.image_read(anat['full']['inv2'])
  full_inv2_bias_corrected = ants.n3_bias_field_correction(full_inv2)
  anat['full']['inv2_bc'] =   anat['full']['inv2'].replace('.nii.gz','_bc.nii.gz')
  ants.image_write(full_inv2_bias_corrected, anat['full']['inv2_bc'])


  # intensity based skull stripping of inv2_bc
  strip_results_intensity_based = nighres.brain.intensity_based_skullstripping(
      main_image=anat['full']['inv2_bc'],
      noise_model='exponential',
      skip_zero_values=True,
      iterate=True,
      dilate_mask=-2,
      save_data=False
  )

  # get the mask from the results of the intensity based skullstripping
  inv2_bc_brain_mask = ants.from_nibabel(strip_results_intensity_based['brain_mask'])



  # # mp2rage skull stripping (very bad, only for comparison)
  # strip_results_mp2rage = nighres.brain.mp2rage_skullstripping(
  #                             second_inversion=anat['full']['inv2_bc'],
  #                             t1_weighted=anat['full']['T1w'],
  #                             t1_map=anat['full']['T1map'],
  #                             save_data=False)

  # anat['full']['T1w_bc_mp2rage_brain_mask'] = reg_dir + 'ses_01/anat/full_inv2_bc_mp2rage_brain_mask.nii.gz'
  # nib.save(strip_results_mp2rage['brain_mask'], anat['full']['T1w_bc_mp2rage_brain_mask'])



  # T1w bias correction
  full_T1w = ants.image_read(anat['full']['T1w'])
  full_T1w_bias_corrected = ants.n3_bias_field_correction(full_T1w)

  # mask the T1w_bc with the brain_mask obtained from the inv2_bc
  full_T1w_brain = full_T1w * inv2_bc_brain_mask


  # save the main T1w_bc, the brain version and the brain mask
  ants.image_write(full_T1w_bias_corrected, reg_dir + 'ses_01/anat/full_T1w.nii.gz')
  ants.image_write(full_T1w_brain, reg_dir + 'ses_01/anat/full_T1w_brain.nii.gz')
  ants.image_write(inv2_bc_brain_mask, reg_dir + 'ses_01/anat/full_T1w_brain_mask.nii.gz')


  # Produce an image of the mask for QC
  produce_png_T1w(sub, full_T1w_bias_corrected, inv2_bc_brain_mask)




# ------------------- Functional (mean) skull stripping -----------------------
def skullstrip_functional(sub, ses, taskrun, func, reg_dir):

  # Calculate mean of the functional 4D
  mean_func_nb = mean_img(func[ses][taskrun])

  mean_func = ants.from_nibabel(mean_func_nb)
  mean_func_norm = ants.iMath(mean_func, 'Normalize')

  # Threshold and get mask. Sub 8 and 9 need a more strict threshold
  if sub == 8 or sub == 9:
    thr = 0.1
  else:
    thr = 0.05

  mean_func_norm_thr = ants.utils.threshold_image(mean_func_norm, low_thresh=thr, binary=False)
  mean_func_norm_thr_mask = ants.get_mask(mean_func_norm_thr, cleanup=1)

  # mask the mean_func with the mean_func_norm_thr_mask
  mean_func_brain = mean_func * mean_func_norm_thr_mask


  # save mean_func_brain and its mask
  ants.image_write(mean_func, reg_dir + 'ses_{:02d}/func/{}_mean.nii.gz'.format(ses,taskrun))
  ants.image_write(mean_func_brain, reg_dir + 'ses_{:02d}/func/{}_mean_brain.nii.gz'.format(ses,taskrun))
  ants.image_write(mean_func_norm_thr_mask, reg_dir + 'ses_{:02d}/func/{}_mean_brain_mask.nii.gz'.format(ses,taskrun))

  # Produce an image of the results for QC
  produce_png_func(
      sub, ses, taskrun, reg_dir,
      ants.n3_bias_field_correction(mean_func),
      mean_func_norm_thr_mask
  )



# ------------------- T123 skull stripping ------------------------------------
def skullstrip_T123(sub, ses, anat, reg_dir):

  # delete volumes 3,5,7 in nibabel
  inv2_nb = nib.load(anat['part'][ses]['inv2'])
  inv2_nb_good = np.delete(inv2_nb.get_fdata(), [2,4,6], axis=3)

  # get the mean of the good volumes in inv2
  inv2_nb_good_mean = np.mean(inv2_nb_good, axis=3)
  inv2_nb_good_mean_nifti = nib.Nifti1Image(inv2_nb_good_mean, inv2_nb.affine)
  inv2_mean = ants.from_nibabel(inv2_nb_good_mean_nifti)

  # apply n3 bias correction to the inv2_mean
  inv2_mean_bc = ants.n3_bias_field_correction(inv2_mean)

  # threshold inv2_mean_bc and get the mask
  thr = 1.5e5
  inv2_mean_bc_thr = ants.utils.threshold_image(inv2_mean_bc, low_thresh=thr, binary=False)
  inv2_mean_bc_thr_mask = ants.get_mask(inv2_mean_bc_thr, cleanup=1)

  # load the T1w and skullstrip
  T1w = ants.image_read(anat['part'][ses]['T1w'])
  T1w_brain = T1w * inv2_mean_bc_thr_mask

  # n3 and denoise the T1w_brain
  T1w_brain_bc = ants.n3_bias_field_correction(T1w_brain)
  T1w_brain_bc_denoised = ants.iMath(T1w_brain_bc, 'PeronaMalik', 20, 1)

  # write the denoised T1w_brain to disk, as well as its mask
  # (taken from the inv2_mean_bc)
  ants.image_write(T1w, reg_dir + 'ses_{:02d}/anat/part_T1w.nii.gz'.format(ses))
  ants.image_write(T1w_brain_bc_denoised, reg_dir + 'ses_{:02d}/anat/part_T1w_brain.nii.gz'.format(ses))
  ants.image_write(inv2_mean_bc_thr_mask, reg_dir + 'ses_{:02d}/anat/part_T1w_brain_mask.nii.gz'.format(ses))

  # Produce an image of the results for QC
  produce_png_T123(sub, ses, reg_dir, T1w, inv2_mean_bc_thr_mask)



# --------------------------- End of functions --------------------------------
# Launch the whole process for each type (anat,func), session (1,2)
# and task/run combination in each session

# # Define reg_dir for this subject, and create it if not there
# reg_dir = foutroot + 'regdata/sub_{:02d}/'.format(sub)
# if not os.path.isdir(reg_dir):
#         os.makedirs(reg_dir)


# Create directory for QC
os.makedirs(reg_dir + 'QC/skullstrip/images', exist_ok=True)



# Launch the whole process
for ses in [1,2]:  # should be [1,2]

  # Create reg_dir bids directory tree
  for acquisition_type in ['anat', 'func']:
    subdir = reg_dir + 'ses_{:02d}/{}/'.format(ses,acquisition_type)
    if not os.path.isdir(subdir):
      os.makedirs(subdir, exist_ok=True)


  # Fetch rawdata and create the dictionary
  in_dir = finroot + 'sub_{:02d}/ses_{:02d}/'.format(sub,ses)
  anat,func = fetch_data(in_dir,reg_dir,sub,ses)


  # FULL skull stripping
  if ses == 1:
    skullstrip_anatomical(sub,anat,reg_dir)


  # PART (T123) skull stripping
  skullstrip_T123(sub, ses, anat, reg_dir)


  # Functional mean img skull stripping
  ses_taskrun = list(func[ses].keys())
  for taskrun in ses_taskrun:
    skullstrip_functional(sub, ses, taskrun, func, reg_dir)


# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/QC/skullstrip/*.md'.format(reg_dir))
os.system('for i in `find {} -name *.png | sort`; do echo !\[image\]\($i\) >> {}/QC/skullstrip/skullstrip.md; done'.format(reg_dir,reg_dir))
os.system('pandoc --self-contained -f markdown {}/QC/skullstrip/skullstrip.md > {}/QC/skullstrip/skullstrip.html'.format(reg_dir,reg_dir))






### EOF

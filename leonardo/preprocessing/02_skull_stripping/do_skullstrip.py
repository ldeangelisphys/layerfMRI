import argparse
import sys

parser = argparse.ArgumentParser(
                description='Carry out skull stripping of full anat, part anat, mean func',
                epilog='Example: python do_skullstrip.py --sub=2 --outroot=leonardo/layers/'
        )

parser.add_argument("--sub", help="subject numba", type=int)
parser.add_argument("--outroot", help="target root in dir in the SAME datadrive")
parser.add_argument("--dd", help="location on storm, default is /data00/", default='/data00/')


args = parser.parse_args()


if len(sys.argv) < 3:
    parser.print_help()
    print(' ')
    sys.exit(1)



# -------------- User defined parameters ----------------------

# The finroot should be edited only if the source of the bids data changes!
# That's why it's not in the argparse parameters

sub=args.sub

datadrive=args.dd
finroot = datadrive + 'leonardo/layers/rawdata_RPI/'
foutroot = datadrive + args.outroot

# -------------- End of User defined parameters ---------------


# print('datadrive is ' + datadrive)
# print('finroot is ' + finroot)
# print('foutroot is ' + foutroot)


print("Processing subject " + str(sub))
print("rawdata source is " + finroot + 'sub-{:02d}/'.format(sub))
print("target directory is " + foutroot + 'regdata/sub-{:02d}/'.format(sub))
print(" ")

# sys.exit(1)


# Load libraries
import nibabel as nib
import numpy as np
import os,re
import json

import nighres
import ants
from fsl.wrappers import fslmaths
from nipype.interfaces import afni as afni
from nilearn.image import mean_img

from nilearn.datasets import fetch_icbm152_2009

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

    # Fetch template
    icbm = fetch_icbm152_2009()
    icbm['t1_highres'] = foutroot + 'mni_icbm152_nlin_sym_09b/mni_icbm152_t1_tal_nlin_sym_09b_hires.nii'
    icbm['t1_highres_masked'] = icbm['t1'].replace('.nii','_masked.nii')
    icbm['t1_masked'] = icbm['t1'].replace('.nii','_masked.nii')


    return anat,func,icbm


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))



# Produce an image of the brain (part) with the mask overlaid on top
def produce_png_anat(reg_dir,bg_img,mask):
  nii_anat = ants.image_read(bg_img)
  nii_mask = ants.image_read(mask)

  ants.plot(
      nii_anat, overlay=mask, overlay_alpha=0.3,
      overlay_cmap='autumn', axis=1, nslices=32, ncol=8,
      title = 'mask full anat sub {:02d}'.format(sub),
      filename=reg_dir + 'QC/skullstrip/images/full_anat_mask.png'.format(mask),
      dpi=72
  )



# Produce an image of the functional mask for QC
def produce_png_func(ses,taskrun,reg_dir,bg_img,mask):
  nii_anat = ants.image_read(bg_img)
  nii_mask = ants.image_read(mask)

  ants.plot(
      nii_anat, overlay=mask, overlay_alpha=0.3,
      overlay_cmap='autumn', axis=0, nslices=32, ncol=8,
      slices=(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9),
      title = 'mask func sub_{:02d}ses_{:02d}_{}'.format(sub,ses,taskrun),
      filename=reg_dir + 'QC/skullstrip/images/sub_{:02d}_ses_{:02d}_{}.png'.format(sub,ses,taskrun),
      dpi=72
  )







# ------------------- Full Anatomical skull stripping -------------------------
def skullstrip_anatomical(anat,reg_dir):

  # inv2 bias correction
  full_inv2 = ants.image_read(anat['full']['inv2'])
  full_inv2_bias_corrected = ants.n3_bias_field_correction(full_inv2)
  anat['full']['inv2_bc'] = reg_dir + 'ses_01/anat/full_inv2_bc.nii.gz'
  nib.save(full_inv2_bias_corrected, anat['full']['inv2_bc'])


  # T1w bias correction
  full_T1w = ants.image_read(anat['full']['T1w'])
  full_T1w_bias_corrected = ants.n3_bias_field_correction(full_T1w)
  anat['full']['T1w_bc'] = reg_dir + 'ses_01/anat/full_T1w_bc.nii.gz'
  nib.save(full_T1w_bias_corrected, anat['full']['T1w_bc'])


  # # mp2rage skull stripping (very bad, only for comparison)
  # strip_results_mp2rage = nighres.brain.mp2rage_skullstripping(
  #                             second_inversion=anat['full']['inv2_bc'],
  #                             t1_weighted=anat['full']['T1w'],
  #                             t1_map=anat['full']['T1map'],
  #                             save_data=False)

  # anat['full']['T1w_bc_mp2rage_brain_mask'] = reg_dir + 'ses_01/anat/full_inv2_bc_mp2rage_brain_mask.nii.gz'
  # nib.save(strip_results_mp2rage['brain_mask'], anat['full']['T1w_bc_mp2rage_brain_mask'])



  # intensity based skull stripping
  strip_results_intensity_based = nighres.brain.intensity_based_skullstripping(
      main_image=anat['full']['inv2_bc'],
      noise_model='exponential',
      skip_zero_values=True,
      iterate=True,
      dilate_mask=-2,
      save_data=False
  )

  # save the brain mask derived from the full_inv2_bc
  anat['full']['inv2_bc_intensityBased_brain_mask'] = reg_dir + 'ses_01/anat/full_inv2_bc_intensityBased_brain_mask.nii.gz'
  nib.save(strip_results_intensity_based['brain_mask'], anat['full']['inv2_bc_intensityBased_brain_mask'])

  # create the brain version of the full_T1w_bc using the in
  anat['full']['T1w_bc_brain'] = reg_dir + 'ses_01/anat/full_T1w_bc_brain.nii.gz'
  fslmaths(anat['full']['T1w_bc']).mul(anat['full']['inv2_bc_intensityBased_brain_mask']).run(anat['full']['T1w_bc_brain'])

  # Produce an image of the mask for QC
  produce_png_anat(
      reg_dir,
      anat['full']['inv2_bc'],
      anat['full']['inv2_bc_intensityBased_brain_mask']
  )




# ------------------- Functional (mean) skull stripping -----------------------
def skullstrip_functional(func,ses,taskrun,reg_dir):

  # calculate mean of the functional 4D
  mean_func = mean_img(func[ses][taskrun])
  mean_func_filename = reg_dir + 'ses_{:02d}/func/{}_mean.nii.gz'.format(ses,taskrun)
  nib.save(mean_func, mean_func_filename)

  # n3 bias correct the mean functional
  mean_func_bc = ants.n3_bias_field_correction(ants.image_read(mean_func_filename))
  mean_func_bc_filename = mean_func_filename.replace('_mean.nii.gz', '_mean_bc.nii.gz')
  nib.save(mean_func_bc, mean_func_bc_filename)

  # AFNI automask
  func[ses][taskrun + '_brain_mask'] = mean_func_bc_filename.replace('.nii.gz','_brain_mask.nii.gz')
  automask = afni.Automask()
  automask.inputs.in_file = mean_func_bc_filename
  automask.inputs.outputtype = "NIFTI_GZ"
  automask.inputs.out_file = func[ses][taskrun + '_brain_mask']
  automask.inputs.brain_file = func[ses][taskrun + '_brain_mask']
  automask.cmdline
  res = automask.run()

  # Apply the mask
  func[ses][taskrun + '_brain'] = mean_func_bc_filename.replace('.nii.gz','_brain.nii.gz')
  fslmaths(mean_func_bc_filename).mul(func[ses][taskrun + '_brain_mask']).run(func[ses][taskrun + '_brain'])

  # Produce an image of the results for QC
  produce_png_func(
    ses,taskrun,reg_dir,
    mean_func_filename,
    mean_func_bc_filename.replace('.nii.gz','_brain_mask.nii.gz')
  )


  # Remove unnecessary files
  os.remove(mean_func_filename)
  # os.remove(mean_func_bc_filename)



# ------------------- T123 (mean of vol 1,3,5,7) skull stripping --------------
def skullstrip_T123(anat,ses,reg_dir):

  # n3 bias correct the T123_inv2
  anat['part'][ses]['inv2_bc'] = reg_dir + 'ses_{:02d}/anat/part_inv2_bc.nii.gz'.format(ses)
  part_inv2_bc = ants.n3_bias_field_correction(ants.image_read(anat['part'][ses]['inv2']))
  nib.save(part_inv2_bc, anat['part'][ses]['inv2_bc'])


  # AFNI automask
  anat['part'][ses]['inv2_bc_brain_mask'] = anat['part'][ses]['inv2_bc'].replace('.nii.gz','_brain_mask.nii.gz')
  automask = afni.Automask()
  automask.inputs.in_file = anat['part'][ses]['inv2_bc']
  automask.inputs.outputtype = "NIFTI_GZ"
  automask.inputs.out_file = anat['part'][ses]['inv2_bc_brain_mask']
  automask.inputs.brain_file = anat['part'][ses]['inv2_bc_brain_mask']
  automask.cmdline
  res = automask.run()


  # n3 bias correct the T1w
  anat['part'][ses]['T1w_bc'] = reg_dir + 'ses_{:02d}/anat/part_T1w_bc.nii.gz'.format(ses)
  part_inv2_bc = ants.n3_bias_field_correction(ants.image_read(anat['part'][ses]['T1w']))
  nib.save(part_inv2_bc, anat['part'][ses]['T1w_bc'])


  # Apply the mask to the T1w_bc using fslmaths
  anat['part'][ses]['T1w_bc_brain'] = anat['part'][ses]['T1w_bc'].replace('.nii.gz','_brain.nii.gz')
  fslmaths(anat['part'][ses]['T1w_bc']).mul(anat['part'][ses]['inv2_bc_brain_mask']).run(anat['part'][ses]['T1w_bc_brain'])


  # Produce an image of the results for QC
  produce_png_func(
    ses,'T123',reg_dir,
    anat['part'][ses]['T1w_bc'],
    anat['part'][ses]['inv2_bc_brain_mask']
  )



# --------------------------- End of functions --------------------------------
# Launch the whole process for each type (anat,func), session (1,2)
# and task/run combination in each session

# Define reg_dir for this subject, and create it if not there
reg_dir = foutroot + 'regdata/sub_{:02d}/'.format(sub)
if not os.path.isdir(reg_dir):
        os.makedirs(reg_dir)


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
  anat,func,templ = fetch_data(in_dir,reg_dir,sub,ses)


  # FULL skull stripping
  if ses == 1:
    skullstrip_anatomical(anat,reg_dir)


  # PART (T123) skull stripping
  skullstrip_T123(anat,ses,reg_dir)


  # Functional mean img skull stripping
  ses_taskrun = list(func[ses].keys())
  for taskrun in ses_taskrun:
    skullstrip_functional(func,ses,taskrun,reg_dir)


# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/QC/skullstrip/*.md'.format(reg_dir))
os.system('for i in `find {} -name *.png`; do echo !\[image\]\($i\) >> {}/QC/skullstrip/skullstrip.md; done'.format(reg_dir,reg_dir))
os.system('pandoc --self-contained -f markdown {}/QC/skullstrip/skullstrip.md > {}/QC/skullstrip/skullstrip.html'.format(reg_dir,reg_dir))





### EOF

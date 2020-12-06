import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Apply fmri <- part <- full <- MNI transformation',
                epilog='Example: python do_apply_transformation.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba", type=int)

args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)



# -------------- User defined parameters ----------------------

sub=args.sub

# Limit the number of threads to 5, cuz many subjs in parallel
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = '1'

# -------------- End of User defined parameters ---------------






# ----------------------------  Load libraries  -------------------------------

import numpy as np
import ants
import nibabel as nib
from fsl.wrappers import fslmaths
import warnings
import os
import shutil
import json
warnings.filterwarnings("ignore")


bd = '/data00/layerfMRI/'
regdir = bd + 'regdata/'
comptx_dir = regdir + 'sub_{:02d}/reg/'.format(sub)


# ----------------------------  Auxiliary functions  --------------------------

# Load all the data required for registration, that is:
# - MNI
# - dizio_fmri
def load_data(sub):

  # create dict for fmri
  list_taskrun = ['task_1_run_1', 'task_1_run_2', 'task_2_run_1', 'task_2_run_2',
                  'task_3_run_1', 'task_3_run_2', 'task_4_run_1', 'task_4_run_2']
  dizio_fmri = {}
  for ses in [1,2]:
    dizio_fmri['ses_{:02d}'.format(ses)] = {}
    for taskrun in list_taskrun:
      fmri_filename = regdir + 'sub_{:02d}/ses_{:02d}/func/{}_4D.nii.gz'.format(sub,ses,taskrun)
      if os.path.isfile(fmri_filename):
        dizio_fmri['ses_{:02d}'.format(ses)][taskrun] = fmri_filename
        # print(fmri_filename)

  # Get the skullstripped MNI to do the full --> MNI registration
  from nilearn.datasets import fetch_icbm152_2009
  MNI_nilearn = fetch_icbm152_2009()
  # MNI_nilearn.keys()
  MNI = ants.image_read(MNI_nilearn['t1']) * ants.image_read(MNI_nilearn['mask'])

  return MNI, dizio_fmri


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))


# Function to carry out the transformation for either 4d or mask (scalar)
def do_MNI_fmri_image(fixed, moving, transformation, imtype='4d', interpoltype='linear'):

  dizio_interpol = {
      'nn' : 'nearestNeighbor',
      'linear'  : 'linear',
      'heavymetal' : 'lanczosWindowedSinc'
  }

  if imtype == 'scalar':
    dim = 0
  elif imtype == '4d':
    dim = 3

  MNI_fmri_image = ants.apply_transforms(
    fixed = fixed,
    moving = moving,
    transformlist = transformation,
    interpolator = dizio_interpol[interpoltype],
    imagetype = dim
  )

  return MNI_fmri_image



# ----------------------------  Main process  ---------------------------------

print('Processing subject ' + str(sub))
print(' ')

# Load data
MNI, dizio_fmri = load_data(sub)

pprint(dizio_fmri)


# # for development
# sub=2
# ses=1
# taskrun='task_1_run_1'


# remember to put for ses in [1,2] !!!!!!!!!!!!!!!!!!!!!!!!!!!
for ses in [1,2]:

  session = 'ses_{:02d}'.format(ses)

  for taskrun in dizio_fmri[session].keys():

    # define the files we need
    fmri_filename = dizio_fmri[session][taskrun]
    mask_filename = regdir  + 'sub_{:02d}/{}/func/{}_mean_brain_mask.nii.gz'.format(sub,session,taskrun)
    transformation_filename = comptx_dir + 'MNI_fmri_{}_{}_comptx.nii.gz'.format(session,taskrun)

    print(fmri_filename)

    # # ------------ take only the first three volumes to speed up the test ---------
    # fmri_full_nib = nib.load(fmri_filename)
    # fmri_part_nib = fmri_full_nib.get_fdata()[:,:,:,0:10]
    # fmri_nib = nib.Nifti1Image(fmri_part_nib, fmri_full_nib.affine)

    # fmri = ants.from_nibabel(fmri_nib)


    # ------------ now let's apply it to the whole time series --------------------
    fmri = ants.image_read(fmri_filename)


    # Transform the 4D
    print('applying transformation to 4D...')
    MNI_fmri_4D_image = do_MNI_fmri_image(
        fixed = MNI,
        moving = fmri,
        transformation = transformation_filename,
        imtype = '4d',
        interpoltype = 'linear'
    )

    # Remove the initial fmri to save memory
    del fmri

    # transform the mask
    mask = do_MNI_fmri_image(
        fixed = MNI,
        moving = ants.image_read(mask_filename),
        transformation = transformation_filename,
        imtype = 'scalar',
        interpoltype = 'nn'
    )

    # Masking with fslmaths, requires takin the images to nibabel
    print('applying mask to the transformed 4D using fslmaths...')

    # write tmp images to load in nibabel, since ANTsPy leaves a lot of
    # stuff in /tmp when converting to nibabel
    tmp_MNI_filename = dizio_fmri[session][taskrun].replace(taskrun,taskrun + '_tmp_MNI')
    tmp_MNI_mask_filename = dizio_fmri[session][taskrun].replace(taskrun,taskrun + '_tmp_MNI_mask')

    ants.image_write(MNI_fmri_4D_image, tmp_MNI_filename)
    ants.image_write(mask, tmp_MNI_mask_filename)


    MNI_fmri_4D_image_nib_masked = (
        (
            fslmaths(nib.load(tmp_MNI_filename))
                    .mul(nib.load(tmp_MNI_mask_filename))
                    .run()
        )
    )


    # Remove MNI_fmri_4D_image and mask to save memory
    del MNI_fmri_4D_image
    del mask


    # write the image
    output_filename = dizio_fmri[session][taskrun].replace('4D.nii.gz','4D_MNI.nii.gz')

    print('writing image to disk...')
    nib.save(MNI_fmri_4D_image_nib_masked, output_filename)

    # Remove MNI_fmri_4D_image_nib_masked to save memory
    del MNI_fmri_4D_image_nib_masked
    os.remove(tmp_MNI_filename)
    os.remove(tmp_MNI_mask_filename)

    print('all done')
    print(' ')





# EOF

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

# -------------- End of User defined parameters ---------------


os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = '1'

print('Processing subject ' + str(sub))
print(' ')


# ----------------------------  Load libraries  -------------------------------

import numpy as np
import ants
import nibabel as nib
import warnings
import os
import shutil
import json
warnings.filterwarnings("ignore")


bd = '/data00/leonardo/layers/'
rawdir = bd + 'rawdata_RPI/'
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
      fmri_filename = rawdir + 'sub_{:02d}/ses_{:02d}/func/sub_{:02d}_ses_{:02d}_{}.nii.gz'.format(sub,ses,sub,ses,taskrun)
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


# Mask a 4D image with a binary mask
# (how simple in python...)
def maskant4D(image4D, mask):
  img4D_nib = image4D.to_nibabel()
  mask_nib = mask.to_nibabel().get_fdata()

  howmanySon = img4D_nib.shape[3]
  multi_mask = np.repeat(mask_nib[:,:,:,np.newaxis], howmanySon, axis=3)

  img4D_nib_masked = nib.Nifti1Image(
      img4D_nib.get_fdata() * multi_mask,
      img4D_nib.affine
  )

  img4D_masked = ants.from_nibabel(img4D_nib_masked)

  return img4D_masked


# ----------------------------  Main process  ---------------------------------

# Load data
MNI, dizio_fmri = load_data(sub)


for ses in [1,2]:
  session = 'ses_{:02d}'.format(ses)
  for taskrun in dizio_fmri[session].keys():

    # define the files we need
    fmri_filename = dizio_fmri[session][taskrun]
    mask_filename = regdir  + 'sub_{:02d}/{}/func/{}_mean_brain_mask.nii.gz'.format(sub,session,taskrun)
    transformation_filename = comptx_dir + 'MNI_fmri_{}_{}_comptx.nii.gz'.format(session,taskrun)

    print(fmri_filename)

    # load the fmri[session][taskrun] 4D image
    print('loading 4D...')
    fmri = ants.image_read(fmri_filename)


    # Transform the 4D
    print('applying transformation...')
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


    # mask the 4D with the binary mask
    print('masking the transformed 4D...')
    MNI_fmri_4D_image_masked = maskant4D(MNI_fmri_4D_image, mask)

    # remove the non-skullstripped MNI_fmri_4D_image and mask to save memory
    del MNI_fmri_4D_image
    del mask


    # write the image
    output_filename = (
        dizio_fmri[session][taskrun]
        .replace('rawdata_RPI','regdata')
        .replace('sub_{:02d}_ses_{:02d}_'.format(sub,ses),'')
        .replace('.nii.gz','_4D_MNI.nii.gz')
    )

    ants.image_write(MNI_fmri_4D_image_masked, output_filename)
    del MNI_fmri_4D_image_masked

    print('all done')
    print(' ')



# EOF

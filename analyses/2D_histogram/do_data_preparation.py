import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Create average depth and layers in MNI across subs',
                epilog='Example: python do_estimate_transformation.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba", type=int)

args = parser.parse_args()


if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)


# ------------------ User defined parameters ----------------------------------

# Params to pass to the py script
sub=args.sub
desired_registration_algorithm = 'SyN'  # SyN or SyNCC (<-very time consuming)
desired_interpolation = 'linear'

# Interpolation can be one of the following:
#
# linear
# nearestNeighbor
# genericlabel
# gaussian
# bSpline
# cosineWindowedSinc
# welchWindowedSinc
# hammingWindowedSinc
# lanczosWindowedSinc


regdata_dir = '/data00/layerfMRI/regdata'

# Limit the number of threads to 5, cuz many subjs in parallel
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "5"


# ------------------ End of user defined parameters ---------------------------




# ----------------------------  Load libraries  -------------------------------

import numpy as np
import ants
import os
import json
import warnings
warnings.filterwarnings("ignore")


# ----------------------------  Auxiliary functions  --------------------------

# Function to fetch the data and create the dictionary
# - T1brain
# - cortical depth
# - MNI_brain

def load_data(sub,regdata_dir):

  anat = {}

  for contrast in ['T1w_brain', 'depth', 'layers']:

    # look for T1w_brain
    entry_T1w = regdata_dir + '/sub_{:02d}/ses_01/anat/full_{}.nii.gz'.format(sub,contrast)
    if os.path.isfile(entry_T1w):
      anat[contrast] = entry_T1w

    # look for depth and layers
    entry_layering = regdata_dir + '/sub_{:02d}/ses_01/anat/layering/LH_layering_layering-{}.nii.gz'.format(sub,contrast)
    if os.path.isfile(entry_layering):
      anat[contrast] = entry_layering


  # Get the skullstripped MNI to do the MNI <-- full registration
  from nilearn.datasets import fetch_icbm152_2009
  MNI_nilearn = fetch_icbm152_2009()
  # MNI_nilearn.keys()
  MNI_brain = ants.image_read(MNI_nilearn['t1']) * ants.image_read(MNI_nilearn['mask'])

  return MNI_brain, anat


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))


# ----------------------------  Registration functions  -----------------------

def do_MNI_full(MNI_brain, full):

  print('registering MNI_brain <-- {}'.format(full))

  MNI_full = ants.registration(
      fixed = MNI_brain,
      moving = ants.image_read(full),
      type_of_transform = desired_registration_algorithm
  )

  return MNI_full



def apply_registration(contrast, MNI_target, save_nii=True):

  contrast_image = ants.image_read(anat[contrast])

  MNI_contrast_image = ants.apply_transforms(
    fixed = MNI_target,
    moving = contrast_image,
    transformlist = MNI_full['fwdtransforms'],
    interpolator = desired_interpolation
  )

  if save_nii:
    anat['{}_MNIspace'.format(contrast)] = anat[contrast].replace('{}.nii.gz'.format(contrast),'{}_MNIspace.nii.gz'.format(contrast))
    ants.image_write(MNI_contrast_image, anat['{}_MNIspace'.format(contrast)])
    pprint(anat)

  return MNI_contrast_image



# ----------------------------  Launch the whole process  ---------------------

# Load sub data and MNI_brain
MNI_brain, anat = load_data(sub, regdata_dir)


# Register full <-- MNI
MNI_full = do_MNI_full(MNI_brain, anat['T1w_brain'])

# apply the transformation to depth and layers
depth_MNIspace = apply_registration(
    contrast='depth',
    MNI_target=MNI_brain,
    save_nii = True
)

layers_MNIspace = apply_registration(
    contrast='layers',
    MNI_target=MNI_brain,
    save_nii = True
)



# The following lines are to produce figures within the notebook
#
# T1w_brain_MNIspace = apply_registration(
#     contrast='T1w_brain',
#     MNI_target=MNI_brain,
#     save_nii=False
# )
#
#
# # image in native space
# ants.plot(
#     image = ants.image_read(anat['T1w_brain']),
#     overlay = ants.image_read(anat['depth']),
#     axis = 1, nslices = 16, ncol = 4,
#     overlay_cmap = 'terrain',    # terrain, cubehelix
#     overlay_alpha = 1,
#     figsize = 4, crop=True,
#     title='Native space'
# )
#
#
# # image in MNI space
# ants.plot(
#     image = T1w_brain_MNIspace,
#     overlay = depth_MNIspace,
#     axis = 1, nslices = 16, ncol = 4,
#     overlay_cmap = 'terrain', overlay_alpha = 1,
#     figsize = 4, crop=True,
#     title='MNI space'
# )





# EOF

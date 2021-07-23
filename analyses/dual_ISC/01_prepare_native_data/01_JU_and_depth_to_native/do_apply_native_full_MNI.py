import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Generate depth and atlas in native space - to be run with conda layerfMRI',
                epilog='Example: python do_apply_native_full_MNI.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba", type=int)
parser.add_argument("--nThreads", help="numba of threads for each subject, default = 5", default="5")


args = parser.parse_args()


if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)



# -------------- User defined parameters ----------------------

# The finroot should be edited only if the source of the bids data changes!
# That's why it's not in the argparse parameters

# nb : sub ID (e.g 2)
# py script : args.sub
sub=args.sub

bd = '/data00/layerfMRI/'
subdir = bd + '/regdata/sub_{:02d}/'.format(sub)
depth_file = subdir + "/ses_01/anat/layering/" + "LH_layering_layering-depth.nii.gz"

gitdir = bd + '/Github_repo/layerfMRI/'
atlas_file = gitdir + "/analyses/dual_ISC/01_prepare_native_data/01_registration/juelich_atlas/" + "atlas_juelich_icbm.nii.gz"

targetdir = gitdir + '/analyses/dual_ISC/data_native/sub_{:02d}/'.format(sub)

# nb : 50
# py script : args.nThreads (5)
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = args.nThreads

# -------------- End of User defined parameters ---------------

"""
Take the juelich atlas and the cortical depth maps in native space

I need:

1. composite registrations :
subdir + "/reg/fmri_MNI/" + taskrun + "_fmri_MNI_comptx.nii.gz"
subdir + "/reg/fmri_full/" + taskrun + "_fmri_full_comptx.nii.gz"

2. depth maps in full space :
subdir + "/ses_01/anat/layering/" + "LH_layering_layering-depth.nii.gz"

3. julich atlas in MNI space :
gitdir + "/analyses/dual_ISC/01_prepare_native_data/01_registration/juelich_atlas/" + atlas_juelich_icbm.nii.gz

"""




# ----------------------------  Load libraries  -------------------------------

import numpy as np
import ants
import shutil
import json
import warnings
warnings.filterwarnings("ignore")


# ----------------------------  Auxiliary functions  --------------------------
# Create the dict with all the composite transformation for each task and run
def create_dizio_reg():
  dizio_reg = {
      "fmri_MNI" : {},
      "fmri_full" : {}
  }

  for task in [1,2,3,4]:
    for run in [1,2]:
      taskrun = 'task_{}_run_{}'.format(task,run)

      # load fmri_MNI comptx
      fmri_MNI_taskrun = subdir + 'reg/fmri_MNI/' + taskrun + '_fmri_MNI_comptx.nii.gz'
      if os.path.isfile(fmri_MNI_taskrun):
        dizio_reg["fmri_MNI"][taskrun] = fmri_MNI_taskrun

      # load fmri_full comptx
      fmri_full_taskrun = subdir + 'reg/fmri_full/' + taskrun + '_fmri_full_comptx.nii.gz'
      if os.path.isfile(fmri_full_taskrun):
        dizio_reg["fmri_full"][taskrun] = fmri_full_taskrun

  return dizio_reg


# Create a dict with all the mean fmri images in native space
# I need it for the ants.apply_transforms)
def create_dizio_fmri_mean():
  dizio_fmri_mean = {}

  for task in [1,2,3,4]:
    for run in [1,2]:
      taskrun = 'task_{}_run_{}'.format(task,run)
      for ses in ['ses_01', 'ses_02']:
        entry = subdir + '{}/func/{}_mean_brain.nii.gz'.format(ses,taskrun)
        if(os.path.isfile(entry)):
          dizio_fmri_mean[taskrun] = entry

  return dizio_fmri_mean


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))



# ----------------- Take depth in native space  -------------------------------

# The 'nearestNeighbor' interpolator was chosen as:
# - the distribution of depth values is (obviously) the same as in the full space
# - all the other methods, including linear, produce fringes, especially in the
#   sulci
# - because of this, all other methods overestimate low values and underestimate
#   high values

# There is a piece of code below which will produce images for each method in the
# notebook.

# The genericLabel takes forever (because depth is continous) and therefore was
# left out of the tests.


def depth2native(taskrun, interpol):

  # print some sanity check
  which_mean_fmri = dizio_fmri_mean[taskrun].split('/')[-1]
  which_comptx = dizio_reg['fmri_full'][taskrun].split('/')[-1]
  print('{} <-- {} <-- depth'.format(which_mean_fmri, which_comptx))

  # read the depth and fmri_mean_brain, and define the target
  depth = ants.image_read(depth_file)
  fmri_mean_image = ants.image_read(dizio_fmri_mean[taskrun])
  targetfile = '{}/depth/sub_{:02d}_depth_{}.nii.gz'.format(targetdir,sub,taskrun)

  # carry out the transformation
  nii = ants.apply_transforms(
      fixed = fmri_mean_image,
      moving = depth,
      transformlist = dizio_reg['fmri_full'][taskrun],
      whichtoinvert = None,
      interpolator = interpol
  )

  # write the resulting image
  ants.image_write(nii, targetfile)

  # produce QC image
  ants.plot(
      image = fmri_mean_image,
      overlay = nii, overlay_alpha=1,
      figsize=6, ncol=14,
      axis=1, nslices=14,
      cbar=True, cbar_length=0.5, cbar_vertical=False, cbar_dx=0.12,
      crop=False,
      title = taskrun + ' ' + interpol, title_dy = -0.15,
      filename = QC_native + '/images/A_sub_{:02d}_depth_{}.png'.format(sub,taskrun),
      dpi=72
  )

  return nii


# ----------------- Take atlas in native space  -------------------------------
#
# I choose 'genericLabel' as interpolator since the multiLabel's result is
# more compact, but it includes some smoothing which might alter the topography
# of the regions

def atlas2native(taskrun, interpol):

  # print some sanity check
  which_mean_fmri = dizio_fmri_mean[taskrun].split('/')[-1]
  which_comptx = dizio_reg['fmri_MNI'][taskrun].split('/')[-1]
  print('{} <-- {} <-- atlas'.format(which_mean_fmri, which_comptx))

  # read the atlas and fmri_mean_brain, and define the target
  atlas = ants.image_read(atlas_file)
  fmri_mean_image = ants.image_read(dizio_fmri_mean[taskrun])
  targetfile = '{}/atlas/sub_{:02d}_atlas_{}.nii.gz'.format(targetdir,sub,taskrun)

  # carry out the transformation
  nii = ants.apply_transforms(
      fixed = fmri_mean_image,
      moving = atlas,
      transformlist = dizio_reg['fmri_MNI'][taskrun],
      whichtoinvert = None,
      interpolator = interpol
  )

  # write the resulting image
  ants.image_write(nii, targetfile)

  # produce QC image
  ants.plot(
      image = fmri_mean_image,
      overlay = nii, overlay_alpha=1,
      figsize=6, nslices=3,
      cbar=True, cbar_length=0.5, cbar_vertical=False, cbar_dx=0.12,
      crop=False,
      title = taskrun + ' ' + interpol, title_dy = -0.15,
      filename = QC_native + '/images/B_sub_{:02d}_atlas_{}.png'.format(sub,taskrun),
      dpi=72
  )


  return nii


# ----------------- Launch the whole process  ---------------------------------
#
# Create dict for the comptx registration warps and the fmri_mean_brain
dizio_reg = create_dizio_reg()
dizio_fmri_mean = create_dizio_fmri_mean()


# Create directory for QC of these operations
QC_native = subdir + '/QC/native_space'
os.makedirs(QC_native + '/images', exist_ok=True)


# Create directory structure of targetdir/[depth/atlas]
for datatype in ['depth','atlas']:
  os.makedirs(targetdir + datatype, exist_ok=True)


# Bring the depth map into native space
for taskrun in dizio_fmri_mean.keys():
  depth2native(taskrun, 'nearestNeighbor')

print(' ')

# Bring the atlas into native space
for taskrun in dizio_fmri_mean.keys():
  atlas2native(taskrun, 'genericLabel')



# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/*.md'.format(QC_native))
os.system('rm {}/*.html'.format(QC_native))
os.system('for i in `find {}/images -name *.png | sort`; do echo !\[image\]\($i\) >> {}/native_space.md; done'.format(QC_native,QC_native))
os.system('pandoc --self-contained -f markdown {}/native_space.md > {}/native_space.html'.format(QC_native,QC_native))




















# EOF

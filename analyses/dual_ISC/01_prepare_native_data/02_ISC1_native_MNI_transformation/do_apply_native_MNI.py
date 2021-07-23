import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description = 'Take a generic MNI-space labelmap into native space - to be run with conda layerfMRI',
                epilog = 'Example: python do_apply_native_MNI.py --sub=2 ' +
                         '--labelmap_file="loo_isc_M_OR_S_No001_k50_bin.nii.gz" ' +
                         '--labelmap_stub="M_OR_S" ' +
                         '--labelmap_folder="ISC" ',
                formatter_class=argparse.RawDescriptionHelpFormatter
        )

parser.add_argument("--sub", help="subject numba", type=int)
parser.add_argument("--labelmap_filename", help="original filename of the labelmap in MNI space")
parser.add_argument("--labelmap_stub", help="stub for this labelmap")
parser.add_argument("--labelmap_folder", help="dir name in /dual_ISC/data_native/ containing the labelmaps in native space")


args = parser.parse_args()


if len(sys.argv) < 5:
    parser.print_help()
    print(' ')
    sys.exit(1)



# -------------- User defined parameters ----------------------

# nb : sub ID (e.g 2)
# py script : args.sub
sub=args.sub


# the following are specific for each labelmap (e.g. for each labelmap from ISC)
labelmap_original_filename = args.labelmap_filename # filename by Lorenzo
labelmap_stub = args.labelmap_stub  # to use a simple name instead of the original labelmap name
labelmap_folder = args.labelmap_folder # name of folder to create inside /data_native/

# -------------- End of User defined parameters ---------------


bd = '/data00/layerfMRI/'
subdir = bd + '/regdata/sub_{:02d}/'.format(sub)

gitdir = bd + '/Github_repo/layerfMRI/'
labelmap_file = gitdir + "/analyses/dual_ISC/01_prepare_native_data/02_ISC1_native_MNI_transformation/" + labelmap_original_filename

targetdir = gitdir + '/analyses/dual_ISC/data_native/sub_{:02d}/'.format(sub)

# nb : 50
# py script : args.nThreads (5)
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "5"


"""
Take a generic MNI-space labelmap into native space

I need:

1. composite registrations :
subdir + "/reg/fmri_MNI/" + taskrun + "_fmri_MNI_comptx.nii.gz"

2. labelmap in MNI space :
gitdir + "/analyses/dual_ISC/01_prepare_native_data/02_ISC1_native_MNI_transformation/" + "loo_isc_M_OR_S_No001_k50_bin.nii.gz"
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
      "fmri_MNI" : {}
  }

  for task in [1,2,3,4]:
    for run in [1,2]:
      taskrun = 'task_{}_run_{}'.format(task,run)

      # load fmri_MNI comptx
      fmri_MNI_taskrun = subdir + 'reg/fmri_MNI/' + taskrun + '_fmri_MNI_comptx.nii.gz'
      if os.path.isfile(fmri_MNI_taskrun):
        dizio_reg["fmri_MNI"][taskrun] = fmri_MNI_taskrun

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



# ----------------- Take labelmap in native space  ----------------------------
#
# I choose 'genericLabel' as interpolator since the multiLabel's result is
# more compact, but it includes some smoothing which might alter the topography
# of the regions

# taskrun = 'task_1_run_1'
# interpol = 'genericLabel'

def labelmap2native(taskrun, interpol):

  # print some sanity check
  which_mean_fmri = dizio_fmri_mean[taskrun].split('/')[-1]
  which_comptx = dizio_reg['fmri_MNI'][taskrun].split('/')[-1]
  print('{} <-- {} <-- {}'.format(which_mean_fmri, which_comptx, labelmap_stub))

  # read the labelmap and fmri_mean_brain, and define the target
  labelmap = ants.image_read(labelmap_file)
  fmri_mean_image = ants.image_read(dizio_fmri_mean[taskrun])
  targetfile = ('{}/{}/{}/sub_{:02d}_{}_{}.nii.gz'
                .format(targetdir,labelmap_folder,labelmap_stub,sub,labelmap_stub,taskrun))

  # carry out the transformation
  nii = ants.apply_transforms(
      fixed = fmri_mean_image,
      moving = labelmap,
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
      filename = QC_native + '/images/B_sub_{:02d}_{}_{}.png'.format(sub,labelmap_stub,taskrun),
      dpi=72
  )


  return nii


# ----------------- Launch the whole process  ---------------------------------
#
# Create dict for the comptx registration warps and the fmri_mean_brain
dizio_reg = create_dizio_reg()
dizio_fmri_mean = create_dizio_fmri_mean()


# Create directory for QC of these operations
QC_native = subdir + '/QC/native_space_ISC'
os.makedirs(QC_native + '/images', exist_ok=True)


# Create directory structure of targetdir/[labelmap_folder]
os.makedirs(targetdir + labelmap_folder + "/" + labelmap_stub, exist_ok=True)


# Bring the labelmap into native space
for taskrun in dizio_fmri_mean.keys():
  labelmap2native(taskrun, 'genericLabel')




# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/*.md'.format(QC_native))
os.system('rm {}/*.html'.format(QC_native))
os.system('for i in `find {}/images -name *.png | sort`; do echo !\[image\]\($i\) >> {}/native_space.md; done'.format(QC_native,QC_native))
os.system('pandoc --self-contained -f markdown {}/native_space.md > {}/native_space.html'.format(QC_native,QC_native))





















# EOF

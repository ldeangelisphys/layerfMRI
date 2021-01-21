import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Registration fmri <- part <- full <- MNI',
                epilog='Example: do_estimate_native_full_MNI.py --sub=2'
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

bd='/data00/layerfMRI/regdata/'

# nb : 50
# py script : args.nThreads (5)
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = args.nThreads

# -------------- End of User defined parameters ---------------



# print('datadrive is ' + datadrive)
# print('finroot is ' + finroot)
# print('foutroot is ' + foutroot)


print('Processing subject ' + str(sub))
print('Using {} threads'.format(args.nThreads))
print('Working dir is ' + bd + 'sub-{:02d}/'.format(sub))
print(' ')

# sys.exit(1)


# ----------------------------  Load libraries  -------------------------------

import numpy as np
import ants
import shutil
import json
import warnings
warnings.filterwarnings("ignore")


# ----------------------------  Auxiliary functions  --------------------------

# Load all the data required for registration, that is:
# - MNI
# - full anatomy
# - dizio_part
# - dizio_fmri
def load_data(sub):

  # Load the full anatomy (there is only one so we can load it directly)
  full_filename = bd + 'sub_{:02d}/ses_01/anat/full_T1w_brain.nii.gz'.format(sub)
  full = ants.image_read(full_filename)

  # create dict for part
  dizio_part = {}
  for ses in [1,2]:
    dizio_part['ses_{:02d}'.format(ses)] = {}
    part_filename = bd + 'sub_{:02d}/ses_{:02d}/anat/part_T1w_brain.nii.gz'.format(sub,ses)
    if os.path.isfile(part_filename):
      dizio_part['ses_{:02d}'.format(ses)] = part_filename
      # print(part_filename)

  # create dict for fmri
  list_taskrun = ['task_1_run_1', 'task_1_run_2', 'task_2_run_1', 'task_2_run_2',
                  'task_3_run_1', 'task_3_run_2', 'task_4_run_1', 'task_4_run_2']
  dizio_fmri = {}
  for ses in [1,2]:
    dizio_fmri['ses_{:02d}'.format(ses)] = {}
    for taskrun in list_taskrun:
      fmri_filename = bd + 'sub_{:02d}/ses_{:02d}/func/{}_mean_brain.nii.gz'.format(sub,ses,taskrun)
      if os.path.isfile(fmri_filename):
        dizio_fmri['ses_{:02d}'.format(ses)][taskrun] = fmri_filename
        # print(fmri_filename)

  # Get the skullstripped MNI to do the MNI <-- full registration
  from nilearn.datasets import fetch_icbm152_2009
  MNI_nilearn = fetch_icbm152_2009()
  # MNI_nilearn.keys()
  MNI = ants.image_read(MNI_nilearn['t1']) * ants.image_read(MNI_nilearn['mask'])

  return MNI, full, dizio_part, dizio_fmri


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))



# ----------------------------  Registration functions  -----------------------

# full <-- MNI
def do_full_MNI(full, MNI):

  # requires find_Warp_Affine(fwd_inv)

  full_MNI = ants.registration(
      fixed = full,
      moving = MNI,
      type_of_transform = 'SyN'
  )

  print('completed full <-- MNI')

  canned_MNI = full_MNI['warpedmovout'].iMath('Canny', 3,1,1).smooth_image(1).threshold_image(0.1,1)

  ants.plot(
      image = full,
      overlay = canned_MNI,
      overlay_cmap = 'autumn', overlay_alpha = 1,
      slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4,
      filename = bd + 'sub_{:02d}/QC/inv_registration/images/fig001_sub_{:02d}_full_MNI.png'.format(sub,sub),
      title = 'full <-- MNI', dpi=72
  )

  return full_MNI



# part[session] <-- full
def do_part_full(session, part, full):

  # Initial [part <-- part] "translation" (it does virtually nothing)
  tx_identity = ants.registration(full, full, type_of_transform="Translation")

  # final
  part_full = ants.registration(
      fixed = part,
      moving = full,
      type_of_transform = "SyN",
      initial_transform = tx_identity['fwdtransforms'][0]
  )

  print('completed part_full session {}'.format(session))

  canned_part_full = part_full['warpedmovout'].iMath('Canny', 3,1,1).smooth_image(0.8).threshold_image(0.1,1)

  ants.plot(
      image = part,
      overlay = canned_part_full,
      overlay_cmap = 'autumn', ncol=4, figsize=3,
      filename = bd + 'sub_{:02d}/QC/inv_registration/images/fig002_sub_{:02d}_part_full_{}.png'.format(sub,sub,session),
      title = 'part <-- full session {}'.format(session), dpi=72
  )

  return part_full



# fmri[session][taskrun] <-- part[session]
def do_fmri_part(session, taskrun, fmri, part):

  # do bias correction of fmri before registration to part
  fmri_bc = ants.n3_bias_field_correction(fmri)
  # print('done N3 bias correction of mean fmri')

  fmri_part = ants.registration(
    fixed = fmri_bc,
    moving = part,
    type_of_transform="SyNBoldAff"
  )

  print('completed fmri_part session {} taskrun {}'.format(session,taskrun))

  canned_fmri_part = fmri_part['warpedmovout'].iMath('Canny', 3,1,1).smooth_image(0.5).threshold_image(0.1,1)

  ants.plot(
    image = fmri,
    overlay = canned_fmri_part,
    overlay_cmap = 'autumn', overlay_alpha = 1,
    slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=3,
    filename = bd + 'sub_{:02d}/QC/inv_registration/images/fig003_sub_{:02d}_fmri_part_{}.png'.format(sub,sub,taskrun),
    title = 'fmri <-- part taskrun {}'.format(taskrun), dpi=72
  )

  return fmri_part



# Save the composites in /reg
def do_save_composite_transformation(fmri_part, part_full, full_MNI, sub, taskrun):

  # fmri <-- part <-- full <-- MNI
  tx_fmri_MNI = fmri_part['fwdtransforms'] + part_full['fwdtransforms'] + full_MNI['fwdtransforms']

  targetdir = bd + 'sub_{:02d}/reg/fmri_MNI'.format(sub)
  os.makedirs(targetdir, exist_ok=True)

  composite_tx_filename = targetdir + '/' + taskrun + '_fmri_MNI_'

  fmri_MNI_transformation = ants.apply_transforms(
      fixed = fmri,
      moving = MNI,
      transformlist = tx_fmri_MNI,
      whichtoinvert=None,
      compose = composite_tx_filename
  )



  # fmri <-- part <-- full
  tx_fmri_full = fmri_part['fwdtransforms'] + part_full['fwdtransforms']

  targetdir = bd + 'sub_{:02d}/reg/fmri_full'.format(sub)
  os.makedirs(targetdir, exist_ok=True)

  composite_tx_filename = targetdir + '/' + taskrun + '_fmri_full_'

  fmri_full_transformation = ants.apply_transforms(
      fixed = fmri,
      moving = full,
      transformlist = tx_fmri_full,
      whichtoinvert=None,
      compose = composite_tx_filename
  )



# Launch the whole process

# Load all the data required for the registration
MNI, full, dizio_part, dizio_fmri = load_data(sub)

# Create directory for QC of registration
QC_invreg = bd + 'sub_{:02d}/QC/inv_registration'.format(sub)
if os.path.isdir(QC_invreg):
  shutil.rmtree(QC_invreg)
os.makedirs(QC_invreg + '/images', exist_ok=True)


# register full <-- MNI
full_MNI = do_full_MNI(full, MNI)


# register part[session] <-- full
for session in ['ses_01','ses_02']:
  part = ants.image_read(dizio_part[session])
  part_full = do_part_full(session, part, full)

  # register part[session] <-- fmri[session][taskrun]
  for taskrun in dizio_fmri[session]:
    fmri = ants.image_read(dizio_fmri[session][taskrun])
    fmri_part = do_fmri_part(session, taskrun, fmri, part)

    # save the composite fmri <-- MNI and fmri <-- full
    do_save_composite_transformation(fmri_part, part_full, full_MNI, sub, taskrun)


# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/*.md'.format(QC_invreg))
os.system('rm {}/*.html'.format(QC_invreg))
os.system('for i in `find {}/images -name *.png | sort`; do echo !\[image\]\($i\) >> {}/registration.md; done'.format(QC_invreg,QC_invreg))
os.system('pandoc --self-contained -f markdown {}/registration.md > {}/registration.html'.format(QC_invreg,QC_invreg))





# EOF

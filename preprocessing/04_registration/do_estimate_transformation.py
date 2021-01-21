import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Registration fmri <- part <- full <- MNI',
                epilog='Example: python do_estimate_transformation.py --sub=2'
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

sub=args.sub

bd = '/data00/layerfMRI/regdata/'

# Limit the number of threads to 5, cuz many subjs in parallel
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
import warnings
import os
import shutil
import json
warnings.filterwarnings("ignore")


# ----------------------------  Auxiliary functions  --------------------------

# Load all the data required for registration, that is:
# - MNI
# - full anatomy
# - dizio_part
# - dizio_fmri
def load_data(sub):

  # Get the skullstripped MNI to do the MNI <-- full registration
  from nilearn.datasets import fetch_icbm152_2009
  MNI_nilearn = fetch_icbm152_2009()
  # MNI_nilearn.keys()
  MNI = ants.image_read(MNI_nilearn['t1']) * ants.image_read(MNI_nilearn['mask'])


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

  return MNI, full, dizio_part, dizio_fmri


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))



# --------------- Auxiliary Registration-specific functions  ------------------
# In the output of ants.registration, the order of warp and affine is reversed
# in fwdtransforms and invtransforms:
#
# fwdtransforms : [warp, affine]
# invtransforms : [affine, warp]
#
# In order to cp the tmp file to the final destination, it is therefore too
# risky to use only the idx [0,1] or [1,0] respectively.
# This function loops on both 'fwdtransforms' or 'invtransforms' strings
# and finds which element of each string contains 'Warp' or 'Affine'.
# In this way the correct pointer to either the Warp or Affine tmp file
# is identified and can be correctly copied to the final sub_[N]/reg destination
#
# The function is used inside MNI_full, part_full and fmri_part registrations

def find_Warp_Affine(fwd_inv):
  warp = [warp for warp in fwd_inv if 'Warp' in warp][0]
  aff = [aff for aff in fwd_inv if 'Affine' in aff][0]
  return warp,aff



# ----------------------------  Registration functions  -----------------------

# MNI <-- full (SyN)
def do_MNI_full(MNI, full, save_nii=False):

  # requires find_Warp_Affine(fwd_inv)

  MNI_full = ants.registration(
      fixed = MNI,
      moving = full,
      type_of_transform = 'SyN'
  )

  print('completed MNI_full')

  if save_nii:
    ants.image_write(MNI_full['warpedmovout'], bd + 'sub_{:02d}/ses_01/anat/MNI_full_SyN.nii.gz'.format(sub))


  # Figure for QC
  canned_MNI = MNI.iMath('Canny', 3,1,1).smooth_image(0.8).threshold_image(0.1,1)

  ants.plot(
    image = MNI_full['warpedmovout'],
    overlay = canned_MNI,
    overlay_cmap = 'autumn', overlay_alpha = 1,
    slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4, dpi=72,
    filename = bd + 'sub_{:02d}/QC/registration/images/fig001_sub_{:02d}_MNI_full.png'.format(sub,sub),
    title='MNI <-- full'
  )


  # Save the transformation files full_part
  TO_FROM = "MNI_full"
  txdir = bd + 'sub_{:02d}/reg/{}'.format(sub,TO_FROM)
  os.makedirs(txdir, exist_ok=True)

  for direction in ['fwdtransforms','invtransforms']:
    print(direction)
    warp, aff = find_Warp_Affine(eval(TO_FROM)[direction])

    warp_target = '{}_Warp.nii.gz'.format(direction)
    shutil.copy(warp, txdir + '/' + warp_target)

    aff_target = '{}_Affine.mat'.format(direction)
    shutil.copy(aff, txdir + '/' + aff_target)

    print(' {} --> {}/{} \n {} --> {}/{}'.format(warp, TO_FROM, warp_target, aff, TO_FROM, aff_target))
    print(' ')

  return MNI_full



# full <-- part[session] (SyN)
def do_full_part(session, full, part, save_nii=False):

  # requires find_Warp_Affine(fwd_inv)

  # Full and part are already similarly aligned, however since they have
  # different FOV, the initial translation carried out by all kinds of
  # registration - shifts the images to a very disaligned position.
  # To work around this problem, I carry out an initial
  # [part <-- part] "translation", which effectively does virtually nothing
  # and then use the resulting affine - close to an identity - to initialize
  # the SyN

  # Initial [part <-- part] "translation" (it does virtually nothing)
  tx_identity = ants.registration(part, part, type_of_transform="Translation")

  # final
  full_part = ants.registration(
      fixed = full,
      moving = part,
      type_of_transform = "SyN",
      initial_transform = tx_identity['fwdtransforms'][0]
  )

  print('completed full_part session {}'.format(session))

  if save_nii:
    ants.image_write(full_part['warpedmovout'], bd + 'sub_{:02d}/{}/anat/full_part.nii.gz'.format(sub,session))


  # Figure for QC
  canned_full_part = full_part['warpedmovout'].iMath('Canny', 3,1,1).smooth_image(0.8).threshold_image(0.1,1)

  ants.plot(
      image = full, overlay = canned_full_part,
      overlay_cmap = 'autumn', slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4,
      filename = bd + 'sub_{:02d}/QC/registration/images/fig002_sub_{:02d}_full_part_{}.png'.format(sub,sub,session),
      title='full <-- part  {}'.format(session), dpi=72
  )


  # Save the transformation files full_part
  TO_FROM = "full_part"
  txdir = bd + 'sub_{:02d}/reg/{}'.format(sub,TO_FROM)
  os.makedirs(txdir, exist_ok=True)

  for direction in ['fwdtransforms','invtransforms']:
    print(direction)
    warp, aff = find_Warp_Affine(eval(TO_FROM)[direction])

    warp_target = '{}_{}_Warp.nii.gz'.format(session,direction)
    shutil.copy(warp, txdir + '/' + warp_target)

    aff_target = '{}_{}_Affine.mat'.format(session,direction)
    shutil.copy(aff, txdir + '/' + aff_target)

    print(' {} --> {}/{} \n {} --> {}/{}'.format(warp, TO_FROM, warp_target, aff, TO_FROM, aff_target))
    print(' ')


  return full_part



# part[session] <-- fmri[session][taskrun]  (SyNBoldAff)
def do_part_fmri(session, taskrun, part, fmri, save_nii=False):

  # requires find_Warp_Affine(fwd_inv)

  # do bias correction of fmri before registration to part
  fmri_bc = ants.n3_bias_field_correction(fmri)

  part_fmri = ants.registration(
    fixed = part,
    moving = fmri_bc,
    type_of_transform="SyNBoldAff"
  )

  print('completed full_part session {} taskrun {}'.format(session,taskrun))

  if save_nii:
    ants.image_write(part_fmri['warpedmovout'], bd + 'sub_{:02d}/{}/func/part_fmri_{}.nii.gz'.format(sub,session,taskrun))

  # Figures for QC
  # canny
  canned_part = part.iMath('Canny', 3,1,1).smooth_image(0.5).threshold_image(0.1,1)

  ants.plot(
      image = part_fmri['warpedmovout'],
      overlay = canned_part,
      overlay_cmap = 'autumn', overlay_alpha = 1,
      slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4, dpi=72,
      filename = bd + 'sub_{:02d}/QC/registration/images/fig003_sub_{:02d}_part_fmri_{}.png'.format(sub,sub,taskrun),
      title='part <-- fmri  {}  {}'.format(session, taskrun)
  )

  # Save the transformation files full_part
  TO_FROM = "part_fmri"
  txdir = bd + 'sub_{:02d}/reg/{}'.format(sub,TO_FROM)
  os.makedirs(txdir, exist_ok=True)

  for direction in ['fwdtransforms','invtransforms']:
    print(direction)
    warp, aff = find_Warp_Affine(eval(TO_FROM)[direction])

    warp_target = '{}_{}_Warp.nii.gz'.format(taskrun,direction)
    shutil.copy(warp, txdir + '/' + warp_target)

    aff_target = '{}_{}_Affine.mat'.format(taskrun,direction)
    shutil.copy(aff, txdir + '/' + aff_target)

    print(' {} --> {}/{} \n {} --> {}/{}'.format(warp, TO_FROM, warp_target, aff, TO_FROM, aff_target))
    print(' ')

  # # olay
  # ants.plot(
  #     image = part.iMath('PeronaMalik', 20,5),
  #     overlay = part_fmri['warpedmovout'].iMath("Normalize").threshold_image(0.1, binary=False),
  #     overlay_cmap = "tab10",
  #     overlay_alpha = 0.7,
  #     slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4, dpi=72,
  #     filename = bd + 'sub_{:02d}/QC/registration/images/fig003_sub_{:02d}_part_fmri_{}_olay.png'.format(sub,sub,taskrun)
  # )

  return part_fmri



# save the composite MNI <-- full <-- part <-- fmri and its inverse
def do_save_composite_transformation(MNI_full, full_part, part_fmri):

  # --------------------    MNI <-- full <-- part <-- fmri   --------------------

  tx_MNI_fmri = MNI_full['fwdtransforms'] + full_part['fwdtransforms'] + part_fmri['fwdtransforms']

  MNI_fmri_transformation = ants.apply_transforms(
      fixed = MNI, moving = fmri,
      transformlist = tx_MNI_fmri,
      whichtoinvert=None,
      compose = transformations_dir + 'MNI_fmri_{}_{}_'.format(session,taskrun)
  )

  # # Figure for QC
  # MNI_fmri_image = ants.apply_transforms(
  #     fixed=MNI, moving=fmri,
  #     transformlist=MNI_fmri_transformation,
  #     interpolator = 'lanczosWindowedSinc', # 'linear','lanczosWindowedSinc'
  # )

  # canned_MNI = ants.iMath(MNI, 'Canny', 3,1,1).smooth_image(0.8).threshold_image(0.1,1)
  # ants.plot(
  #     image = MNI_fmri_image.n3_bias_field_correction().iMath('Normalize'), overlay = canned_MNI,
  #     overlay_cmap = 'autumn', slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4
  # )




  # --------------------    fmri <-- part <-- full <-- MNI   --------------------

  fmri_part = part_fmri['invtransforms']
  part_full = full_part['invtransforms']
  full_MNI = MNI_full['invtransforms']

  tx_fmri_MNI = fmri_part + part_full + full_MNI

  fmri_MNI_transformation = ants.apply_transforms(
      fixed = fmri, moving = MNI,
      transformlist = tx_fmri_MNI,
      whichtoinvert=[True,False,True,False,True,False],
      compose = transformations_dir + 'fmri_MNI_{}_{}_'.format(session,taskrun)
  )

  # # Figure for QC
  # fmri_MNI_image = ants.apply_transforms(
  #     fixed=fmri, moving=MNI,
  #     transformlist=fmri_MNI_transformation,
  #     interpolator = 'lanczosWindowedSinc', # 'linear','lanczosWindowedSinc'
  # )

  # ants.plot(
  #     image = fmri_MNI_image, overlay=fmri.iMath('Normalize'),
  #     overlay_alpha=0.3,
  #     slices = tuple(np.arange(0.2,0.4,0.03)[0:6]), ncol=3, figsize=4
  # )

  return





# ----------------------------  Launch the whole process  ---------------------
# Load all the data required for the registration
MNI, full, dizio_part, dizio_fmri = load_data(sub)
# pprint(dizio_fmri)


# Create directory to store composite transformations
transformations_dir = bd + 'sub_{:02d}/reg/'.format(sub)
if not os.path.isdir(transformations_dir):
  os.makedirs(transformations_dir)


# Create directory for QC of registration
QC_reg = bd + 'sub_{:02d}/QC/registration'.format(sub)
if os.path.isdir(QC_reg):
  shutil.rmtree(QC_reg)
os.makedirs(QC_reg + '/images', exist_ok=True)


# register full <-- MNI
MNI_full = do_MNI_full(MNI, full)


# register full <-- part[session]
for session in ['ses_01','ses_02']:
  part = ants.image_read(dizio_part[session])
  full_part = do_full_part(session, full, part)

  # register part[session] <-- fmri[session][taskrun]
  for taskrun in dizio_fmri[session]:
    fmri = ants.image_read(dizio_fmri[session][taskrun])
    part_fmri = do_part_fmri(session, taskrun, part, fmri)

    # save the composite MNI <-- fmri and the inverse fmri <-- MNI
    do_save_composite_transformation(MNI_full, full_part, part_fmri)


# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
os.system('rm {}/*.md'.format(QC_reg))
os.system('rm {}/*.html'.format(QC_reg))
os.system('for i in `find {}/images -name *.png | sort`; do echo !\[image\]\($i\) >> {}/registration.md; done'.format(QC_reg,QC_reg))
os.system('pandoc --self-contained -f markdown {}/registration.md > {}/registration.html'.format(QC_reg,QC_reg))




# EOF

import argparse
import sys

parser = argparse.ArgumentParser(
                description='Reconstruct T1w and T1map from MP2RAGE and T123',
                epilog='Example: python do_MP2RAGE_reconstruction.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba", type=int)


args = parser.parse_args()


if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)

# -------------- User defined parameters ----------------------

sub=args.sub  

finroot='/data01/layerfMRI/rawdata_RPI'

# -------------- End of User defined parameters ---------------

print("Processing subject " + str(sub))
print("rawdata source is " + finroot + '/sub-{:02d}'.format(sub))
print(" ")



import nighres
import nibabel as nib
from nilearn.image import mean_img
import numpy as np
import os


# -------------------- Functions ---------------------------------------
# Function to fetch the data and create the dictionary
def fetch_data(finroot):

  anat = {}
  for a in ['full','part']:
      anat[a] = {}
      for ses in [1,2]:
          anat[a][ses] = {}
          for n in ['inv1','inv1ph','inv2','inv2ph','T1w','T1map']:
              entry = finroot + '/sub_{:02d}/ses_{:02d}/anat/sub_{:02d}_ses_{:02d}_acq_{}_{}.nii.gz'.format(sub,ses,sub,ses,a,n)
              if os.path.isfile(entry):
                  anat[a][ses][n] = entry

  # There is only one session for full, so I delete the level associated to the ses
  if len(anat['full'][1]) > 0:
      anat['full'] = anat['full'][1]
  elif len(anat['full'][2]) > 0 :
      anat['full'] = anat['full'][2]

  return anat



def full_reconstruction():

  result = nighres.intensity.mp2rage_t1_mapping(
              first_inversion=[anat['full']['inv1'],anat['full']['inv1ph']],
              second_inversion=[anat['full']['inv2'],anat['full']['inv2ph']],
              inversion_times=[0.8,2.7],
              flip_angles=[7.0,5.0],
              inversion_TR=6.2,
              excitation_TR=[0.0062, 0.0062],
              N_excitations=160,
              efficiency=0.96,
              correct_B1=False,
              B1_map=None,
              scale_phase=True,
              save_data=False
          )

  return result



def part_reconstruction(ses):

  partone={}

  for acq in ['inv1','inv1ph','inv2','inv2ph']:
    nii = nib.load(anat['part'][ses][acq])
    # delete all volumes but the first,
    # otherwise we will have bad noise in the T1w due to motion
    firstvol = np.delete(nii.get_fdata(), [1,2,3,4,5,6,7], axis=3)
    nii_firstvol = nib.Nifti1Image(firstvol, nii.affine)
    partone[acq] = nii_firstvol

  result = nighres.intensity.mp2rage_t1_mapping(
              first_inversion=[partone['inv1'], partone['inv1ph']],
              second_inversion=[partone['inv2'], partone['inv2ph']],
              inversion_times=[0.8,2.7],
              flip_angles=[7.0,5.0],
              inversion_TR=6.2,
              excitation_TR=[0.052, 0.052],
              N_excitations=160,
              efficiency=0.96,
              correct_B1=False,
              B1_map=None,
              scale_phase=True,
              save_data=False
          )

  return result



# This below was the reconstruction taking the mean of all "good" images
# However since there is no motion correction between scans, this causes
# some bad noise in the final T1w. Therefore I decided to use only the first
# volume.
# Motion correction would be very hard to carry out since it would required
# to have exactly the same transformation in inv1, inv1ph, inv2 and inv2ph
#
# def part_reconstruction(ses):
#
#   partmean={}
#
#   for acq in ['inv1','inv1ph','inv2','inv2ph']:
#     nii = nib.load(anat['part'][ses][acq])
#     # delete volumes 2,4,7
#     niigood = np.delete(nii.get_fdata(), [2,4,6], axis=3)
#     niigood_mean = np.mean(niigood, axis=3)
#     nii_niigood_mean = nib.Nifti1Image(niigood_mean, nii.affine)
#     partmean[acq] = nii_niigood_mean
#
#   result = nighres.intensity.mp2rage_t1_mapping(
#               first_inversion=[partmean['inv1'], partmean['inv1ph']],
#               second_inversion=[partmean['inv2'], partmean['inv2ph']],
#               inversion_times=[0.8,2.7],
#               flip_angles=[7.0,5.0],
#               inversion_TR=6.2,
#               excitation_TR=[0.052, 0.052],
#               N_excitations=160,
#               efficiency=0.96,
#               correct_B1=False,
#               B1_map=None,
#               scale_phase=True,
#               save_data=False
#           )
#
#   return result


# -------------------- End of functions --------------------------------



anat = fetch_data(finroot)

# Reconstruct FULL T1 and T1map
fullreco = full_reconstruction()
nib.save(fullreco['uni'], anat['full']['inv1'].replace('inv1','T1w'))
nib.save(fullreco['t1'], anat['full']['inv1'].replace('inv1','T1map'))


# Reconstruct PARTIAL T1 and T1map
# NB: although the part anat were created using numpy, they are stored in
#     the dict as nifti images with a proper affine
for ses in [1, 2]:
  partreco = part_reconstruction(ses)
  print(ses)
  # partreco['uni'].orthoview()
  nib.save(partreco['uni'], anat['part'][ses]['inv1'].replace('inv1','T1w'))
  nib.save(partreco['t1'], anat['part'][ses]['inv1'].replace('inv1','T1map'))







## EOF

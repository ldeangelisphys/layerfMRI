import argparse
import sys
import os

parser = argparse.ArgumentParser(
                description='Reconstruct layers using nighres',
                epilog='Example: python do_layering.py --sub=2'
        )

parser.add_argument("--sub", help="subject numba NON zeropadded", type=int)

args = parser.parse_args()

if len(sys.argv) < 2:
    parser.print_help()
    print(' ')
    sys.exit(1)

# --------------  User defined parameters  ------------------------------------

sub=args.sub

rawdata_dir = '/data01/layerfMRI/rawdata_RPI'
regdata_dir = '/data00/layerfMRI/regdata'

# Limiting the numba of cores used by ants
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = '5'

# NOTA BENE:
#
# The results now go in the regdata_dir, since they are not super heavy - about
# 1.6 GB per subject.
# However in the next future we can also send them to rawdata_dir. That's why
# this code is still here and not down in the 'Launch everything' section.

# Create a layering dir in the rawdata_RPI, and delete a previous one to start anew
layering_dir = regdata_dir + '/sub_{:02d}/ses_01/anat/layering'.format(sub)

if not os.path.isdir(layering_dir):
        os.makedirs(layering_dir)

# Create directory for QC - same reason as above
QCdir = regdata_dir + '/sub_{:02d}/QC/layering'.format(sub)
os.makedirs(QCdir + '/images', exist_ok=True)


# Specify whether the results should be overwritten in nighres functions
OVERWRITE_FLAG = False


# --------------  End of User defined parameters  -----------------------------



import nighres
import nibabel as nib
import ants
from nilearn.image import mean_img
import numpy as np
import os
import json
from fsl.wrappers import fslmaths


# --------------  Auxiliary functions  ----------------------------------------

# Function to fetch the data and create the dictionary
def fetch_data(regdata_dir, rawdata_dir):

  anat = {}
  anat['raw'] = {}
  for contrast in ['inv1','inv1ph','inv2','inv2ph']:
      entry_raw = rawdata_dir + '/sub_{:02d}/ses_01/anat/sub_{:02d}_ses_01_acq_full_{}.nii.gz'.format(sub,sub,contrast)
      anat['raw'][contrast] = entry_raw

  return anat


# Pretty print dict
def pprint(dict):
  print(json.dumps(dict, indent=4))


# Dump dict to a text file, to check the last completed stage
logfile = layering_dir + '/000_last_completed_stage.txt'
def create_log(dict):
  with open(logfile,'w') as f:
    f.write(json.dumps(dict, indent=4))


# --------------  Cortical processing functions  ------------------------------


# T1w and T1map reconstruction from MP2RAGE data
#
# MP2RAGE (full)
# - inversion_times (sec) :	     [0.8, 2.7] # provided by Wietske from Examcard
# - flip angles (deg) :  	       INV1 = 7.0	INV2 = 5.0	(flip column in PAR)
# - inversion_TR (sec) :         5.5        # provided by Wietske  from Examcard
# - excitation_TR	(sec) : 	     INV1 = 0.0062	INV2 = 0.0062	(Repetition time in PAR header)
# - N_excitations/slices :       159 # provided by Wietske  from Examcard

def do_reconstruct_T1(anat):

  anat['recon'] = nighres.intensity.mp2rage_t1_mapping(
      [anat['raw']['inv1'], anat['raw']['inv1ph']],
      [anat['raw']['inv2'], anat['raw']['inv2ph']],
      inversion_times = [0.8, 2.7],
      flip_angles = [7.0, 5.0],
      inversion_TR = 5.5,
      excitation_TR = [0.0062, 0.0062],
      N_excitations = 159,
      efficiency = 0.96,
      correct_B1 = False,
      B1_map = None,
      scale_phase = False,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'recon'
  )

  create_log(anat)
  return anat



# Skull stripping
# The intensity based skull stripping of the inv2 doesn't work very well, so we
# prepare it with an N4biasfieldcorrection

def do_skullstrip(anat):

  # Check if the N4 file is already there, otherwise carry out bias field correction
  # Note that we have to create the dict item anyway, and that's why the next
  # command is not limited to the 'else'
  inv2_N4bc_filepath = anat['raw']['inv2'].replace('inv2','inv2_N4bc')

  if not os.path.isfile(inv2_N4bc_filepath):

    command_N4 = 'time N4BiasFieldCorrection -d 3 -i {} -o {} -v'.format(
                      anat['raw']['inv2'],
                      inv2_N4bc_filepath
                  )
    os.system(command_N4)

  anat['raw']['inv2_N4bc'] = inv2_N4bc_filepath



  # Carry out intensity-based skull stripping on the N4-corrected inv2_N4bc
  anat['intensity_strip'] = nighres.brain.intensity_based_skullstripping(
      main_image = anat['raw']['inv2_N4bc'],
      extra_image = anat['recon']['t1'],
      noise_model = 'exponential',
      skip_zero_values = True,
      iterate = True,
      dilate_mask = 3,
      topology_lut_dir = None,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'istrip'
  )


  # I replaced the MP2RAGE skull stripping with the intensity-based
  # skull stripping (see note on top) but I want to keep the same naming
  # conventions, so I just create a 'skullstrip' dictionary - which in the
  # original version output the results of MP2RAGE skull stripping - and
  # map the location of the files created by the intensity-based stripping
  anat['skullstrip'] = {}

  anat['skullstrip']['brain_mask'] = anat['intensity_strip']['brain_mask']
  anat['skullstrip']['inv2_masked'] = anat['intensity_strip']['main_masked']
  anat['skullstrip']['t1map_masked'] = anat['intensity_strip']['extra_masked']

  # calculate and save also the masked T1w, since I had it as an output from the
  # MP2RAGE skull stripping
  anat['skullstrip']['t1w_masked'] = anat['skullstrip']['inv2_masked'].replace('main.nii.gz','t1w.nii.gz')

  if not os.path.isfile(anat['skullstrip']['t1w_masked']):
    (
        fslmaths(anat['recon']['uni'])
        .mul(anat['intensity_strip']['brain_mask'])
        .run(anat['skullstrip']['t1w_masked'])
    )



# Estimate filters for Dura and Ridges
def do_filtering(anat):

  # Dura estimation
  anat['dura'] = nighres.brain.mp2rage_dura_estimation(
      second_inversion = anat['raw']['inv2'],
      skullstrip_mask = anat['skullstrip']['brain_mask'],
      background_distance = 3.0,
      output_type = 'dura_region',
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'dura'
  )


  # Ridge structures
  anat['ridge'] = nighres.filtering.filter_ridge_structures(
      input_image = anat['skullstrip']['t1map_masked'],
      structure_intensity = 'bright',
      output_type = 'probability',
      use_strict_min_max_filter = True,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'ridge'
  )


  # Filter stacking
  anat['filter_stack'] = nighres.brain.filter_stacking(
      dura_img = anat['dura']['result'],
      pvcsf_img = anat['ridge']['result'],
      arteries_img = None,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'filter_stack'
  )

  create_log(anat)
  return anat



# MGDM Segmentation
def do_MGDM(anat):

  # Optional
  ATLAS_DIR = '/home/cerliani/anaconda3/envs/layerfMRI/lib/python3.7/site-packages/nighres/atlases/brain-segmentation-prior3.0'
  atlas_name = 'brain-atlas-quant-3.0.8.txt'
  atlas_filename = os.path.join(ATLAS_DIR, atlas_name)


  # MGDM segmentation
  anat['MGDM'] = nighres.brain.mgdm_segmentation(
      contrast_image1 = anat['skullstrip']['t1map_masked'], contrast_type1 = 'T1map7T',
      contrast_image2 = anat['filter_stack']['result'], contrast_type2 = 'Filters',
      n_steps = 5,
      max_iterations = 500,
      topology = 'wcs',
      atlas_file = None,
      topology_lut_dir = None,
      adjust_intensity_priors = False,
      normalize_qmaps = True,
      compute_posterior = False,
      posterior_scale = 10.0,
      diffuse_probabilities = False,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'mgdm'
  )

  create_log(anat)
  return anat



# LH Region extraction
def do_region_extraction(anat):

  anat['region'] = nighres.brain.extract_brain_region(
      segmentation = anat['MGDM']['segmentation'],
      levelset_boundary = anat['MGDM']['distance'],
      maximum_membership = anat['MGDM']['memberships'],
      maximum_label = anat['MGDM']['labels'],
      extracted_region='left_cerebrum',
      atlas_file = None,
      partial_volume_distance = 1.0,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = 'LH_cortex'
  )

  create_log(anat)
  return anat




# Cruise cortical reconstruction
def do_cruise(anat):

  anat['cruise'] = nighres.cortex.cruise_cortex_extraction(
      init_image = anat['region']['inside_mask'],
      wm_image   = anat['region']['inside_proba'],
      gm_image   = anat['region']['region_proba'],
      csf_image  = anat['region']['background_proba'],
      vd_image = None,
      data_weight = 0.4,
      regularization_weight = 0.1,
      max_iterations = 500,
      normalize_probabilities = True,
      correct_wm_pv = True,
      wm_dropoff_dist = 1.0,
      topology='wcs',
      topology_lut_dir=None,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = "LH_cruise"
  )

  create_log(anat)
  return anat





# Volumetric layering
def do_layering(anat):

  anat['layering'] = nighres.laminar.volumetric_layering(
      inner_levelset = anat['cruise']['gwb'],
      outer_levelset = anat['cruise']['cgb'],
      n_layers = 4,
      topology_lut_dir = None,
      method = 'volume-preserving',
      layer_dir = 'outward',
      curv_scale = 3,
      save_data = True, overwrite = OVERWRITE_FLAG,
      output_dir = layering_dir, file_name = "LH_layering"
  )

  create_log(anat)
  return anat






# --------------  Launch the whole process  -----------------------------------



# Reset the logfile
if os.path.isfile(logfile):
  os.remove(logfile)

# Create the dictionary with the raw data
anat = fetch_data(regdata_dir, rawdata_dir)


# Reconstruct T1w and T1map
do_reconstruct_T1(anat)


# Skull stripping
# includes also some ANTs N4 which allow to carry out MP2RAGE skull stripping
do_skullstrip(anat)


# Estimate Dura and Ridges and prepare the corresponding filter
do_filtering(anat)


# MGDM Segmentation
# Optionally, you can use an atlas prior different from the default one
do_MGDM(anat)


# Extract cortex of the LH
do_region_extraction(anat)


# Cruise cortical reconstruction
do_cruise(anat)


# Create layers and depth map
do_layering(anat)


# Generate QC images
title_skullstrip = 'subj {:02d} skullstrip'.format(sub)
ants.plot(
    image = anat['raw']['inv2'],
    overlay = anat['skullstrip']['brain_mask'], overlay_cmap='autumn', overlay_alpha=0.3,
    axis=2, figsize=6, nslices=20, ncol=5,
    title = title_skullstrip,
    filename = QCdir + '/images/' + title_skullstrip.replace(" ","_") + '.png',
    dpi = 72
)


title_cortex_estimation = 'subj {:02d} cortex estimation'.format(sub)
ants.plot(
    image = anat['skullstrip']['t1w_masked'],
    overlay = anat['cruise']['cortex'], overlay_cmap='Set1', overlay_alpha=0.5,
    axis=2, figsize=6, nslices=15, ncol=5,
    title = title_cortex_estimation,
    filename = QCdir + '/images/' + title_cortex_estimation.replace(" ","_") + '.png',
    dpi = 72
)


title_cortical_depth = 'subj {:02d} cortical depth'.format(sub)
ants.plot(
    image = anat['skullstrip']['t1w_masked'],
    overlay = anat['layering']['depth'], overlay_cmap='jet', overlay_alpha=1,
    axis=2, figsize=6, nslices=15, ncol=5, crop=True,
    title = title_cortical_depth,
    filename = QCdir + '/images/' + title_cortical_depth.replace(" ","_") + '.png', dpi = 72
)

print(" ")
print('There are QC images for {} and {}'.format(title_cortex_estimation, title_cortical_depth))


# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
# Produce the HTML page with the QC (requires pandoc to be installed on the machine with apt get)
if os.path.isfile('{}/layering.md'.format(QCdir)):
  os.system('rm {}/layering.*'.format(QCdir))

os.system('for i in `find {}/images -name *.png | sort`; do echo !\[image\]\($i\) >> {}/layering.md; done'.format(QCdir,QCdir))

os.system('pandoc --self-contained -f markdown {}/layering.md > {}/layering.html'.format(QCdir,QCdir))



# EOF

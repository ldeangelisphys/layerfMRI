

import numpy as np
import nibabel as nib

bd='/Users/leonardo/GoogleDrive/LAYER_fMRI/__PAPER__/figures/fig_2_results_ISC1/'

for contrast in ['M_boot','S_boot', 'M_OR_S_boot']:
    print(contrast)
    img = nib.load(bd + contrast + '.nii.gz')
    data = img.get_fdata()
    data.shape
    hdr = img.header
    newdata = np.zeros(data.shape, dtype=np.float32)
    newimg = nib.Nifti1Image(data, img.affine)
    nib.save(newimg, bd + contrast + '.nii.gz')

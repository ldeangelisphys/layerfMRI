from nilearn import plotting
import matplotlib.pyplot as plt
import os
import nibabel as nib

cwd = os.getcwd()
datadir = os.path.dirname(cwd) + '/Data'


M_boot = nib.load(datadir + '/M_boot.nii.gz')

fig = plt.figure(figsize=(5*1.618, 5), dpi=80)
plotting.plot_glass_brain(M_boot, colorbar=True, figure=fig, vmax = 0.21, display_mode='x')
fig.savefig(os.path.dirname(cwd) + '/FigureElementsPDF/M_boot_glassbrain.pdf', dpi=100)
fig




S_boot = nib.load(datadir + '/S_boot.nii.gz')

fig = plt.figure(figsize=(5*1.618, 5), dpi=80)
plotting.plot_glass_brain(S_boot, colorbar=True, figure=fig, vmax = 0.21, display_mode='x')
fig.savefig(os.path.dirname(cwd) + '/FigureElementsPDF/S_boot_glassbrain.pdf', dpi=100)
fig

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import nibabel as nib
import numpy as np
import os,re
from nilearn import plotting as niplt
from nilearn import image as niimg
from nilearn.masking import apply_mask,unmask,compute_epi_mask
import matplotlib.pyplot as plt
import pymp2rage
import time
import nighres
from nilearn.datasets import fetch_icbm152_2009
from shutil import copyfile
import ants


# In[2]:


datadrive = '/data00/'

finroot = datadrive + 'lorenzo/PROJECTS/layers/rawdata/'
foutroot = datadrive + 'lorenzo/PROJECTS/layers/'


# In[ ]:





# ### Fectch the anatomycal and functional data 

# In[4]:


def fetch_data(in_dir,reg_dir,sub,ses):

    # Fetch anatomical
    if not os.path.isdir(reg_dir):
        os.makedirs(reg_dir)

    anat = {}
    for a in ['full','part']:
        anat[a] = {}
        for ses in [1,2]:
            anat[a][ses] = {}
            for n in ['inv1','inv1ph','inv2','inv2ph','T1w','T1map']:
                entry = finroot + 'sub-{:02d}/ses-{:02d}/anat/sub-{:02d}_ses-{:02d}_acq-{}_{}.nii.gz'.format(sub,ses,sub,ses,a,n)
                if os.path.isfile(entry):
                    anat[a][ses][n] = entry

    # There is only one session for full, so I delete the level associated to the ses
    if len(anat['full'][1]) > 0:
        anat['full'] = anat['full'][1]
    elif len(anat['full'][2]) > 0 :
        anat['full'] = anat['full'][2]
        
    # Fetch functional
    func = {}
    for ses in [1,2]:
        func[ses] = {}
        func_fld = finroot + 'sub-{:02d}/ses-{:02d}/func/'.format(sub,ses)
        func_files = [f for f in os.listdir(func_fld) if 'space-MNI' not in f]
        for f in func_files:
            task = f.split('task-')[1].split('_')[0]
            run  = f.split('run-')[1].split('_')[0]
            func[ses][f'task-{task}_run-{run}'] = func_fld + f
    
    # Fetch template
    icbm = fetch_icbm152_2009()
    icbm['t1_highres'] = foutroot + 'mni_icbm152_nlin_sym_09b/mni_icbm152_t1_tal_nlin_sym_09b_hires.nii'
    icbm['t1_highres_masked'] = icbm['t1'].replace('.nii','_masked.nii')
    icbm['t1_masked'] = icbm['t1'].replace('.nii','_masked.nii')
            
            
    return anat,func,icbm

def plot_slices(image,back_image,cut_direction,nr,cuts,fs,fout,op=0.5,col = 'Reds_r'):

    fig,ax = plt.subplots(nrows = nr,figsize = fs)
    l = int(len(cuts)/nr)
    for i in range(nr):
        row_cuts = cuts[i*l:(i+1)*l]
        niplt.plot_roi(image, bg_img= back_image, display_mode=cut_direction,
                      cut_coords=row_cuts, alpha = op,axes=ax[i],figure=fig,cmap=col,
                      output_file = fout)
    
    plt.close('all')
    print('fslview_deprecated {} {}'.format(back_image,image))
    
    return

def apply_mask(data,label,fname):
    masked = niimg.math_img('im1*im2',
                                im1=data[label],
                                im2=data['brain_mask'])

    data[label+'_masked'] = fname
    nib.save(masked,data[label+'_masked']) 
    
    return

def do_skullstrip(anat,reg_dir,make_plots=True):
    
    skullstripping_results = nighres.brain.mp2rage_skullstripping(
                                            second_inversion=anat['full']['inv2'],
                                            t1_map=anat['full']['T1map'],
                                            t1_weighted=anat['full']['T1w'],
                                            save_data=True,
                                            file_name='full',
                                            output_dir=reg_dir,
                                            overwrite=False)

    anat['full']['T1map_masked'] = reg_dir + 'full_strip-t1map.nii.gz'
    anat['full']['T1w_masked'] = reg_dir + 'full_strip-t1w.nii.gz'
    anat['full']['brain_mask'] = reg_dir + 'full_strip-mask.nii.gz'
    
    for l in ['T1map_masked','T1w_masked','brain_mask']:
        try:
            niimg.index_img(anat['full'][l],0).to_filename(anat['full'][l] )
        except:
            print(f'{l} already 3D')
    if make_plots:
        plot_slices(anat['full']['brain_mask'],anat['full']['T1w'],
                cut_direction = 'z', nr=4,cuts = np.arange(-70,90,2),fs = (20,10),
                fout = reg_dir + 'brain_mask.png')

    return


def mask_part_anat(anat,ses,reg_dir,opn=1,make_plots=True):

    mask_img = compute_epi_mask(anat['part'][ses]['inv2'],opening=opn,lower_cutoff=0.2,upper_cutoff=0.8)
    anat['part'][ses]['brain_mask'] = reg_dir + 'part_epi-mask.nii.gz'
    nib.save(mask_img,anat['part'][ses]['brain_mask'])
    apply_mask(anat['part'][ses],'T1w',reg_dir+'part_ses-{:02d}_T1w_masked.nii.gz'.format(ses))

    if make_plots:
        plot_slices(anat['part'][ses]['brain_mask'],anat['part'][ses]['T1w'],
                    cut_direction = 'x', nr=2,cuts = np.arange(-60,-20,2),fs = (40,10),
                    fout = reg_dir + 'part_ses-{:02d}_brain_mask.png'.format(ses))
        
    return


def reg_part2full(anat,ses,reg,reg_dir,make_plots=True):
    
    full_t1w_resampled = niimg.resample_to_img(anat['full']['T1w_masked'],anat['part'][ses]['T1w_masked'])
    anat['full']['T1w_resampled'] = reg_dir + 'full_ses-{:02d}_T1w_resampled.nii.gz'.format(ses)
    nib.save(full_t1w_resampled,anat['full']['T1w_resampled'])
    
    
    reg['anat2brain_ses-{:02d}'.format(ses)] = nighres.registration.embedded_antsreg(
                            source_image=anat['part'][ses]['T1w_masked'],
                            target_image=anat['full']['T1w_resampled'],
                            run_rigid=True, run_syn=False,run_affine=False,
                            mask_zero=True,
                            rigid_iterations=1000,
                            cost_function='MutualInformation',
                            interpolation='Linear',
                            save_data=True, file_name="part_ses-{:02d}_anat2brain".format(ses),
                            output_dir=reg_dir, overwrite=True)
    if make_plots:
        plot_slices(reg['anat2brain_ses-{:02d}'.format(ses)]['transformed_source'],anat['full']['T1w'],
                cut_direction = 'x', nr=2,cuts = np.arange(-60,-20,2),fs = (40,10),
                fout = reg_dir + 'part_ses-{:02d}-anat2brain.png'.format(ses),col='hot',
                op=0.3)
    return

def reg_brain2mni(anat,templ,reg,reg_dir,make_plots=True,run_syn=True):
    
    full_t1w_resampled = niimg.resample_img(
        anat['full']['T1w_masked'],
        target_affine = nib.load(anat['part'][ses]['T1w']).affine,
        target_shape = nib.load(anat['full']['T1w_masked']).shape
    )
    anat['full']['T1w_resampledfull'] = reg_dir + 'full_ses-{:02d}_T1w_resampledfull.nii.gz'.format(ses)
    nib.save(full_t1w_resampled,anat['full']['T1w_resampledfull'])
    
    reg['brain2mni'] = nighres.registration.embedded_antsreg(
                        source_image=anat['full']['T1w_resampledfull'],
                        target_image=templ['t1_masked'],
                        run_affine=True,
                        run_syn=run_syn,
                        cost_function='MutualInformation',
                        interpolation='Linear',
                        save_data=True, file_name="full_brain2mni",
                        output_dir=reg_dir, overwrite=True)
    if make_plots:
        plot_slices(reg['brain2mni']['transformed_source'],templ['t1_masked'],
                cut_direction = 'z', nr=4,cuts = np.arange(-70,90,2),fs = (40,20),
                fout = reg_dir + 'brain_reg.png', col = 'hot',op=0.3)
    return

def mask_part_func(func,ses,sel,reg_dir,opn=2,make_plots=True):
    
    mask_img = compute_epi_mask(func[ses][sel],opening=opn,lower_cutoff=0.2,upper_cutoff=0.8)
    func[ses][sel + '_mask'] = reg_dir + f'ses-{ses}_{sel}_mask.nii.gz'
    nib.save(mask_img,func[ses][sel + '_mask'])
    
    m_func = niimg.mean_img(func[ses][sel])
    func[ses][sel + '_mean'] = reg_dir + f'ses-{ses}_{sel}_mean.nii.gz'
    nib.save(m_func,func[ses][sel + '_mean'])
    
    mean_masked = niimg.math_img('im1*im2',
                                im1=func[ses][sel + '_mask'],
                                im2=func[ses][sel + '_mean'])

    func[ses][sel + '_mean_masked'] = reg_dir + f'ses-{ses}_{sel}_mean_masked.nii.gz'
    nib.save(mean_masked,func[ses][sel + '_mean_masked'])
    
    if make_plots:
        plot_slices(func[ses][sel + '_mask'],func[ses][sel + '_mean'],
            cut_direction = 'x', nr=2,cuts = np.arange(-60,-20,2),fs = (40,10),
            fout = reg_dir + 'part_ses-{:02d}_{}_brain_mask.png'.format(ses,sel))
        
    return

def reg_func2part(func,ses,sel,reg_dir,make_plots=True):
    
    reg['func2anat_ses-{:02d}_{}'.format(ses,sel)] = nighres.registration.embedded_antsreg(
                        source_image=func[ses][sel + '_mean_masked'],
                        target_image=anat['part'][ses]['T1w_masked'],
                        run_affine=False, run_syn=False,
                        rigid_iterations=1000,
                        cost_function='MutualInformation',
                        interpolation='NearestNeighbor',
                        save_data=True, file_name="part_ses-{:02d}_{}_func2anat".format(ses,sel),
                        output_dir=reg_dir, overwrite=True)

    if make_plots:
        plot_slices(reg['func2anat_ses-{:02d}_{}'.format(ses,sel)]['transformed_source'],
            anat['part'][ses]['T1w'],
            cut_direction = 'x', nr=2,cuts = np.arange(-60,-20,2),fs = (40,10),
            fout = reg_dir + 'part_ses-{:02d}_{}_func2anat.png'.format(ses,sel),col='hot',
            op=0.3)
    
    return



def apply_all_deformations(func,ses,sel,reg,reg_dir):

    
    dfmdpre = nighres.registration.apply_coordinate_mappings(
        func[ses][sel],
        reg['func2anat_ses-{:02d}_{}'.format(ses,sel)]['mapping'],
        reg['anat2brain_ses-{:02d}'.format(ses)]['mapping'],
        save_data=False
    )
    
    temp_img = niimg.resample_img(
        dfmdpre['result'],
        target_affine = dfmdpre['result'].affine,
        target_shape =  nib.load(anat['full']['T1w_resampledfull']).shape
    )
    temp_fname = reg_dir + 'part_ses-{:02d}_{}_reg_def-res-img.nii.gz'.format(ses,sel)
    temp_img.to_filename(temp_fname)

    dfmdpost = nighres.registration.apply_coordinate_mappings(
        temp_fname,
        reg['brain2mni']['mapping'],
        save_data=False
    )
                                                                                                                                                                             
    fname = reg_dir + 'part_ses-{:02d}_{}_reg_def-img.nii.gz'.format(ses,sel)
    dfmdpost['result'].to_filename(fname)
    
    return {'result':fname}


def apply_all_deformations_iter(func,ses,sel,reg,reg_dir):

    
    dfmdpre = nighres.registration.apply_coordinate_mappings(
        func[ses][sel],
        reg['func2anat_ses-{:02d}_{}'.format(ses,sel)]['mapping'],
        reg['anat2brain_ses-{:02d}'.format(ses)]['mapping'],
        save_data=False
    )
    
    temp_img = niimg.resample_img(
        dfmdpre['result'],
        target_affine = dfmdpre['result'].affine,
        target_shape =  nib.load(anat['full']['T1w_resampledfull']).shape
    )
    temp_fname = reg_dir + 'part_ses-{:02d}_{}_reg_def-res-img.nii.gz'.format(ses,sel)
    temp_img.to_filename(temp_fname)
    
    
    Nvols = temp_img.shape[-1]
    chunk_size = 50
    
    if Nvols%chunk_size == 0:
        Niter = int(Nvols/chunk_size)
    else:
        Niter = int(Nvols/chunk_size)+1


    volumes = []
    for ichunk in range(Niter):
        nst = ichunk*chunk_size
        nen = (ichunk+1)*chunk_size
        print('from {} to {}'.format(nst,nen))
        slim = niimg.index_img(nib.load(temp_fname),slice(nst,nen))

        slim_fname = reg_dir + 'part_ses-{:02d}_{}_reg_def-res-img-{:03d}.nii.gz'.format(ses,sel,ichunk)
        slim.to_filename(slim_fname)

        dfmdpost = nighres.registration.apply_coordinate_mappings(
            slim_fname,
            reg['brain2mni']['mapping'],
            save_data=True,
            file_name="part_ses-{:02d}_{}_reg-{:03d}".format(ses,sel,ichunk),
            output_dir=reg_dir,
            overwrite=True
        )

        volumes.append(dfmdpost['result'])

    full_img = niimg.concat_imgs(volumes)
    fname = reg_dir + 'part_ses-{:02d}_{}_reg_def-img.nii.gz'.format(ses,sel)
    full_img.to_filename(fname)
    
    return {'result':fname}


# In[ ]:





# In[4]:


do_plot = False

for sub in [1,2,3,5,6,7,8,9,10,12,13,14,4,11]:

    reg = {}
    reg_dir = foutroot + 'regdata/sub-{:02d}/'.format(sub)

    for ses in [1,2]:

        in_dir = finroot + 'sub-{:02d}/ses-{:02d}/'.format(sub,ses)
        
        # FULL
        if ses == 1:
            anat,func,templ = fetch_data(in_dir,reg_dir,sub,ses)
            do_skullstrip(anat,reg_dir,make_plots=do_plot)
            reg_brain2mni(anat,templ,reg,reg_dir,run_syn=True,make_plots=do_plot)

            
        # SES
        mask_part_anat(anat,ses,reg_dir,make_plots=do_plot)
        reg_part2full(anat,ses,reg,reg_dir,make_plots=do_plot)
        # FUNC
        funckeys = list(func[ses].keys())
        for sel in funckeys:
            mask_part_func(func,ses,sel,reg_dir,opn=2,make_plots=do_plot)
            reg_func2part(func,ses,sel,reg_dir,make_plots=do_plot)
            st = time.time()
            deformed = apply_all_deformations_iter(func,ses,sel,reg,reg_dir)
            copyfile(deformed['result'],func[ses][sel].replace('_bold','_space-MNI_bold'))
            en = time.time()
            print('Deformed in {:.0f} s'.format(en-st))


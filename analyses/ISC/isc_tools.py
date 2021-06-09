import numpy as np
from scipy.stats import pearsonr
import pandas as pd
import os
from brainiak.isc import isc
import matplotlib.pyplot as plt


def r2numpy(rvec):
    
    return np.array(rvec[2:-1].split(', '),dtype = 'float')

# def trim_movielength(dataf):
    
#     trimmed = dataf['tc_mean_unfolded'][:movie_length[dataf['muvi']]]
    
#     return trimmed
    
    
def stdize(a):
    
    return (a - np.average(a)) / np.std(a)

def generic_isfc(data,intersubject = True):
    """This function computes isfc in the loo approach or a ppi-like connectivity
    
    INPUT
    data: n_TRs x n_roi x n_subjects : time series of the roi and subjects
    intersubject: boolean to decide whether or not to do ISFC or WSFC    
    
    OUTPUT
    fc_data: ISFC or WSFC data (n_subjects x n_roi)
    """
    
    n_TR,n_roi,n_subjects = data.shape

    roi_pair = 0
    fc_data = np.zeros((n_subjects,int(0.5*n_roi*(n_roi-1))),dtype = float)
    for roi1 in range(n_roi):
        for roi2 in range(roi1+1,n_roi):
            if intersubject:
                avg_roi1  = np.sum(data[:,roi1,:],axis=1) / (n_subjects - 1)
                avg_roi2  = np.sum(data[:,roi2,:],axis=1) / (n_subjects - 1)
            for sub in range(n_subjects):
                one_roi1 = data[:,roi1,sub]
                one_roi2 = data[:,roi2,sub]
                if intersubject:
                    loo_roi1 = avg_roi1 - ( one_roi1 / (n_subjects - 1) )
                    loo_roi2 = avg_roi2 - ( one_roi2 / (n_subjects - 1) )
                    fc_data[sub,roi_pair] = ( 
                        pearsonr(one_roi1,loo_roi2)[0] +
                        pearsonr(one_roi2,loo_roi1)[0]
                    )/2
                else:
                    fc_data[sub,roi_pair] = ( 
                        pearsonr(one_roi1,one_roi2)[0]
                    )

            roi_pair += 1
            
    return fc_data


def import_summary_log(froot):
    
    logsumm = (pd
           .read_csv(froot+ 'logs/log_summary.csv')
           .assign(fmri = lambda d:
                   froot + 
                   'regdata/sub_' + d['subject'].apply(lambda n: '{:02d}'.format(n)) +
                   '/ses_' + d['session'].apply(lambda n: '{:02d}'.format(n)) +
                   '/func/task_' + d['task'].apply(lambda n: '{:01d}'.format(n)) +
                   '_run_' + d['run'].apply(lambda n: '{:01d}'.format(n)) +
                   '_4D_MNI.nii.gz'
                  )
           .assign(fmri_missing = lambda d : d['fmri'].apply(lambda s: os.path.isfile(s) != True))
           
          )
    
    return logsumm

def extract_movie_length(logsumm):
    
    movie_length = {}

    for mv in logsumm.Title.unique():
        durations = logsumm.loc[lambda d : d['Title'] == mv]['ExpectedDuration'].unique()
        if len(durations) != 1:
            print('Warning! More than one duration found')
            movie_length[mv] = np.min(durations)
        else:
            movie_length[mv] = durations[0]
            
    return movie_length

def import_timecourse_dataframe(input_file,check_movie_length = True, movie_length = {}):
    """Reads the dataframe with timecourses as exported by the R package.
       Allows for checking that all the movies timecourses have the same (expected) length.
    """
    
    
    # Read dataframe
    df = pd.read_csv(input_file)

    # Transform timecourses into numpy arrays and standardize them
    df['tc_mean_unfolded'] = (df['tc_mean_unfolded']
                              .map(r2numpy)
                             )

    # Correct for movies that are missing the last frame
    df['measured_movl'] = df.apply(lambda row : len(row['tc_mean_unfolded']), axis = 1)
    
    if check_movie_length:
        df['expected_movl'] = df.apply(lambda row : movie_length[row['muvi']], axis = 1)

        corrected_movl = (df
                          .loc[lambda d : d['expected_movl'] > d['measured_movl']]
                          .groupby('muvi')
                          .apply(lambda d: np.min(d['measured_movl']))
                         )

        for m in dict(corrected_movl):
            movie_length[m] = corrected_movl[m]
        #####################################################

        df['tc_mean_trimmed'] = (df
                                 .apply(lambda row : row['tc_mean_unfolded'][:movie_length[row['muvi']]], axis = 1)
                                 .map(stdize)
                                )

        df['measured_movl'] = df.apply(lambda row : len(row['tc_mean_trimmed']), axis = 1)

        
    return df

def average_same_movie_timecourse(dataf,tc_column='tc_mean_trimmed',av_column='muvi'):
    """Given a dataframe with timecourses at the tc_column returns the average across
    the av_column"""

    averaged_movie_dataf = pd.DataFrame()

    for i,mdf in dataf.groupby([av_column]):
        if len(mdf) != 2:
            print('Warning! This movie seems to have {} entries instead of 2.'.format(len(mdf)))
            break

        else:

            entry = mdf.iloc[0][['contrast','sub','JU','D_bins',av_column]]
            entry['run'] = ','.join(np.array(mdf['run'].values,dtype = str))
            entry[tc_column] = np.average(mdf[tc_column])

            averaged_movie_dataf = averaged_movie_dataf.append(entry)

    return averaged_movie_dataf

def concatenate_movies(dataf,average_same_movie=True):
    """Concatenates timecourses of the input dataframe, allowing for average across same movie runs"""
    
    # Get movie names
    movie_names = {}
    for c,gdf in dataf.groupby(['contrast']):
        movie_names[c] = gdf.sort_values(['muvi']).muvi.unique()

    # Concatenate movie and task
    cdf  = pd.DataFrame()
    count = 0

    for [c,s,j,d],gdf in dataf.groupby(['contrast','sub','JU','D_bins']):

        
        #### IF WE WANT TO AVERAGE THE DATA FROM SAME MOVIE ACROSS RUNS
        if average_same_movie:
            gdf = average_same_movie_timecourse(gdf)        
        
        
        gdf = gdf.sort_values(['muvi','run'])
        movie_list = gdf['muvi'].unique()

        try:
            same = (movie_names[c] == movie_list).all()
        except:
            same = False
        if not same:
            print(f'Error! contrast {c} subject {s} JU {j} D_bins {d}')
        else:
            count += 1

        concatenated = np.hstack(gdf['tc_mean_trimmed'])

        temp_df = gdf.iloc[0][['contrast','sub','JU','D_bins']]
        temp_df['tc_concatenated'] = concatenated

        cdf = cdf.append(temp_df)
        
    cdf['D_bins'] = cdf['D_bins'].astype(int)
    cdf['JU'] = cdf['JU'].astype(int)
    cdf = cdf.sort_values(['contrast','sub','JU','D_bins'])
        
    return cdf

def exclude_subjects(dataf,subjects):
    
    for subject in subjects:
        dataf = dataf.loc[lambda d: d['sub'] != subject]
        
    return dataf



def doublecheck_same_lenght(cdf):
    """This checks what length of the concatenated arrays is the most common and delets combinations of JU and Dbins that are different
    """
    for c,contrast_df in cdf.groupby('contrast'):

        T = int(contrast_df['tc_concatenated'].apply(lambda d: len(d)).mode())
        unmatching = contrast_df.loc[contrast_df['tc_concatenated'].apply(lambda d: len(d)) != T][['D_bins','JU']].drop_duplicates()


        for i,unm in unmatching.iterrows():

            cdf = cdf.drop(cdf.loc[lambda d : (d['contrast'] == c)&(d['JU']==unm['JU'])&(d['D_bins']==unm['D_bins'])].index)

            print('Contrast {}: bin {} of JU {} deleted'.format(c,unm['D_bins'],unm['JU']))


        # This checks what length of the concatenated arrays is the most common and delets combinations of JU and Dbins that are different
        grouped_df = contrast_df.groupby(['D_bins','JU']).apply(lambda d:len(d['sub']))
        N_sub = int(grouped_df.mode())
        grouped_df = grouped_df.reset_index()
        unmatching = grouped_df.loc[lambda d: d[0] != N_sub]

        for i,unm in unmatching.iterrows():

            cdf = cdf.drop(cdf.loc[lambda d : (d['contrast'] == c)&(d['JU']==unm['JU'])&(d['D_bins']==unm['D_bins'])].index)

            print('!!Contrast {}: bin {} of JU {} deleted'.format(c,unm['D_bins'],unm['JU']))

    return cdf


def compute_isc(cdf):
    
    isc_column = np.array([])

    for c,contrast_df in cdf.groupby('contrast'):

        iscarr = np.array(list(contrast_df
         .groupby('sub')
         .apply(lambda d: np.array(list(d['tc_concatenated'])).T)
        ))

        iscarr = np.moveaxis(iscarr,0,2)

        isc_data =  isc(iscarr)
        isc_column = np.append(isc_column,isc_data.ravel())

    cdf['isc'] = np.arctanh(isc_column)

    return cdf

def plot_export_isc(cdf,input_file,method):

    ncols = cdf['JU'].nunique()
    nrows = cdf['contrast'].nunique()

    fig,axarr = plt.subplots(ncols=ncols,nrows=nrows, sharex=True, sharey = True, figsize = (ncols*2,5))
    axarr = np.ravel(axarr)

    for i,((c,j),plotdf) in enumerate(cdf.groupby(['contrast','JU'])):   

        plotdf.boxplot(column = ['isc'], by = 'D_bins',ax=axarr[i])
        axarr[i].set_title('JU {}'.format(int(j)))
        axarr[i].set_ylabel('ISC {}'.format(c))

    axarr = axarr.reshape(nrows,ncols)
    for ax in axarr[0]:
        ax.set_xlabel('')
    for ax in axarr[1]:
        ax.set_xlabel('# bin')
    for ax in axarr[:,1:].ravel():
        ax.set_ylabel('')
    for ax in axarr[1]:
        ax.set_title('')

    fig.suptitle('')

    plt.savefig(input_file.replace('.csv','_isc.png'), dpi = 300)
    cdf.to_csv(input_file.replace('.csv','_isc.csv'))
    
    return

    
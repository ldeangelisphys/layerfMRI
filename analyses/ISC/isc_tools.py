import numpy as np

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
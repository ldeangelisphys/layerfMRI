import numpy as np

def r2numpy(rvec):
    
    return np.array(rvec[2:-1].split(', '),dtype = 'float')

# def trim_movielength(dataf):
    
#     trimmed = dataf['tc_mean_unfolded'][:movie_length[dataf['muvi']]]
    
#     return trimmed
    
    
def stdize(a):
    
    return (a - np.average(a)) / np.std(a)


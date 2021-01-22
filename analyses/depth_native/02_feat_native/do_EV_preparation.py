import numpy as np
import pandas as pd
import os,shutil
import glob

bd='/data00/layerfMRI/analyses/PPI'
logs = pd.read_csv(bd + '/log_summary.csv')

datadir='/data00/layerfMRI/regdata'

EVdir = bd + '/EV_predictors'

if os.path.exists(EVdir):
  shutil.rmtree(EVdir)
os.mkdir(EVdir)


# Sub 13 has either problems or will join later
list_sub = [2, 3, 5, 6, 8, 9, 10, 11, 12, 14]


def write_EV(sub,ses,task,run,logs,bd,EVdir,movietype='S'):

  df_onerun = logs[(
    (logs.subject == sub)
    & (logs.session == ses)
    & (logs.task == task)
    & (logs.run == run)
    & (logs.Type == movietype)
  )]

  EV = np.zeros(df_onerun.total_TR.max(), dtype='int')
  for i in range(len(df_onerun)):
    EV[df_onerun.start_TR.iloc[i] - 1 : df_onerun.end_TR.iloc[i] - 1] = 1

  filename = '{}/sub_{:02d}_EV_task_{}_run_{}_{}.txt'.format(EVdir,sub,task,run,movietype)
  print(filename)
  np.savetxt(filename, EV, fmt='%.1d', newline=os.linesep)



for sub in list_sub:
  for ses in [1,2]:
    for task in [1,2,3,4]:
      for run in [1,2]:

        filename = '{}/sub_{:02d}/ses_{:02d}/func/task_{}_run_{}_4D_MNI.nii.gz'.format(datadir,sub,ses,task,run)
        if os.path.isfile(filename):
          print(filename)

          for scrambled_or_motion in ['S','M']:

            write_EV(sub,ses,task,run,logs,bd,EVdir,movietype=scrambled_or_motion)

          print(' ')


import numpy as np
import pandas as pd
import os

import warnings
warnings.filterwarnings("ignore")

pd.set_option("display.max_rows", None, "display.max_columns", None)

bd = '/Users/leonardo/GoogleDrive/LAYER_fMRI/logs/'

TR = 4.1


subj = 'S02'
ses = '1'
set = '1'
run = '1'

logfile = bd + '/clean/' + subj + '_session' + ses + '_set' + set + '_run' + run + '_Set' + set + '_run' + run + '.log'

log = pd.read_csv(logfile, delimiter='\t', skiprows=3)

# extract the list of muviz with their duration. Note that the
# column names are FU since it takes the one from the first df
# in the file
muviz = log[log['Subject'].str.startswith('H')]

f = lambda x: x['Subject'].split("\\")[-1]
muviz['name'] = muviz.apply(f, axis=1)
muviz = muviz[['name','Duration']].reset_index(drop=True)
muviz['nTR'] = muviz['Duration'].astype('int')/1e4/TR
muviz['nTR'] = muviz['nTR'].apply(lambda x: round(x))
muviz



log = log[log['Subject'].str.startswith(subj)]


# There is a Response=4 logged, which appears to simply occur whenever a Pulse
# occurs, and is not interesting for building the EV, therefore we remove it
total_Response4 = log[(log['Event Type'] == 'Response') & (log['Code'] == '1')].shape[0]
total_Pulses = log[log['Event Type'] == 'Pulse'].shape[0]


# Select only the relevant columns, remove rows where Response=4 - which equates
# to removing rows where Code == 4 - and reset the index.
log = (
    log[['Event Type', 'Code', 'Time','Duration']]
    .loc[log['Event Type'] != 'Response']
    .reset_index(drop=True)
)

# log



# Initialize a column for the pulse numba and fill it with the sequential number
# of Pulses. This will be used to keep track of the initial volume/time point to
# assign to each movie
log['Pulse_Numba'] = 0
numba_pulse = len(log[log['Event Type'] == 'Pulse'])
idx_pulse_rows = np.where(log['Event Type'] == 'Pulse')[0]
log['Pulse_Numba'].iloc[idx_pulse_rows] = np.arange(1,numba_pulse+1).astype('int')
# log


# check that the TR is correct - creates a separate 'fog' df
fog = log[log['Event Type'] == 'Pulse']
fog['Time_+1'] = fog['Time'].shift(periods = -1, fill_value = 0)
fog['TR'] = fog['Time_+1'].astype('int') - fog['Time'].astype('int')
# fog['TR']


# log[(log['Event Type'] == 'Video') | (log['Event Type'] == 'Picture')]


# now shift the Pulse_Numba of -1 so that the numba on each video (Action[N])
# corresponds to the starting volume/time point
log['muvi_start_volume'] = log['Pulse_Numba'].shift(periods = -1, fill_value = 0)

log

# isolate the rows with movies
log_vids = log[log['Event Type'] == 'Video'].copy().reset_index(drop=True)

muviz


# remove useless cols and join the information
log_vids = log_vids[['Code','muvi_start_volume']]

log_vids['muvi_end_volume'] = log_vids['muvi_start_volume'] + muviz['nTR'] -1
log_vids['muvi_name'] = muviz['name']
log_vids['nTR'] = muviz['nTR']



# add some additional info for between-sub comparison
sub_ID = subj + '_session' + ses + '_set' + set + '_run' + run + '_Set' + set + '_run' + run

log_vids['sub'] = subj
log_vids['ses'] = ses
log_vids['set'] = set
log_vids['run'] = run

log_vids

# reorder the columns
log_vids = log_vids[['sub','ses','set','run','muvi_name','muvi_start_volume','muvi_end_volume','nTR','Code']]

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

files_dir = '/Users/thomas/Desktop/ok/'

for _, __, files in os.walk(files_dir):

    files = sorted([x for x in files if (('unprocessed' not in x) and ('tick' in x))])

    for file in files:

        file_path = files_dir + file

        df = pd.read_csv(file_path.replace('.csv', '_unprocessed.csv'), names=['time'])
        df['frequency'] = 1/(df['time'].diff().shift(-1)) * 1e9
        df['time_sec'] = (df['time']-df.time[0])/1e9/60
        df2 = pd.read_csv(file_path, names=['time', 'frequency'])
        df2['time_sec'] = (df2['time']-df2.time[0])/1e9/60

        plt.plot(df.time_sec, df.frequency, color='tab:grey', alpha=0.3, label='Raw exp weighted average')
        plt.plot(df2.time_sec, df2.frequency, '-x', alpha=0.5, color='red', label='Filtered and recorded ticklist')
        plt.title(f'From {int(len(df)/(list(df.time_sec)[-1]*60))} to {round(len(df2)/int(list(df2.time_sec)[-1]*60),2)} points/second')
        plt.xlabel('time [min]')
        plt.ylabel('frequency [hz]')
        plt.legend()
        plt.show()
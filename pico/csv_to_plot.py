import numpy as np
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv 
from scipy.signal import butter, filtfilt
import os

# This is working

# Define the low pass filter
cutoff_freq = 0.17
sampling_freq = 4.10
def lowpass_filter(dataframe):
    b, a = butter(5, 2*cutoff_freq/sampling_freq, btype='low', analog=False)
    return filtfilt(b, a, dataframe)

def animate(i):

    # Get the most recent file
    directory = os.getcwd()+'/mqtt_files/'
    files = [f for f in os.listdir(directory)]
    files.sort(reverse=True)
    file_path = files[0]
    
    with open(directory + file_path, 'r') as f:
        data = [row[0] for row in csv.reader(f)] 

    df = pd.DataFrame({'time': data, 'sensor': ['Hall' for x in data]})
    df['time'] = df['time'].apply(lambda x: int(x))

    hall_times = list(df[df.sensor=='Hall'].time)

    for i in range(len(hall_times)-1):
        frequency = 1/(hall_times[i+1]-hall_times[i])*1e9
        if i==0: 
            df.loc[df.time>=0, 'hall_freq'] = frequency/2
            df.loc[df.time>=0, 'hall_GPM'] = frequency/7.5 * 0.264172
        df.loc[df.time>=hall_times[i], 'hall_freq'] = frequency
        df.loc[df.time>=hall_times[i], 'hall_GPM'] = frequency/7.5 * 0.264172

    # Low pass filer
    df['hall_GPM_bias_filtered'] = lowpass_filter(df['hall_GPM'])

    # Exponential weighted average
    alpha = 0.65
    W = [0]*len(df)
    theta = list(df.hall_GPM)
    for t in range(len(df)-1):
        W[t+1] = alpha*W[t] + (1-alpha)*theta[t+1]
    df['hall_GPM_bias_expWA'] = W

    # Get rid of outliers
    upper_limit = 300
    df.loc[df['hall_GPM'] > upper_limit, 'hall_GPM'] = np.nan
    df.loc[df['hall_GPM_bias_filtered'] > upper_limit, 'hall_GPM_bias_filtered'] = np.nan
    df.loc[df['hall_GPM_bias_expWA'] > upper_limit, 'hall_GPM_bias_expWA'] = np.nan
    df['hall_GPM'] = df['hall_GPM'].mask(df['hall_GPM'].isnull()).ffill()
    df['hall_GPM_bias_filtered'] = df['hall_GPM_bias_filtered'].mask(df['hall_GPM_bias_filtered'].isnull()).ffill()
    df['hall_GPM_bias_expWA'] = df['hall_GPM_bias_expWA'].mask(df['hall_GPM_bias_expWA'].isnull()).ffill()
    
    # Clear the current figure before plotting
    plt.cla()

    # Plot results
    #plt.plot(GPM_reciprocal, alpha=0.15, label=f'Hall effect', color='black')
    plt.plot(list(df.time), list(df.hall_freq), alpha=0.85, label=f'Hall effect', color='red')
    #plt.plot(list(df.hall_GPM_bias_expWA), alpha=0.7, label=f'Hall effect, expWA', color='tab:blue')
    #plt.plot(list(df.hall_GPM_bias_filtered), alpha=0.7, label=f'Hall effect, filtered', color='tab:orange')
    plt.ylabel('GPM')
    plt.xlabel('Time')
    plt.grid()

    plt.tight_layout()
    plt.legend()

ani = FuncAnimation(plt.gcf(), animate, interval=10, save_count=100000)
plt.tight_layout()
plt.show()
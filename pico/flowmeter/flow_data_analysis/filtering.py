import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

def process_timestamps(file_path:str, f_s_factor:int=4, f_c:float=1.25, threshold:float=0.1):
    '''
    Filters and collects frequency points from a CSV file containing timestamps.

    This function reads timestamps from a CSV file, computes the time difference between consecutive timestamps,
    applies a low-pass Butterworth filter to smooth the time difference data, converts the filtered data to frequency,
    and then collects frequency points where the difference between consecutive frequencies exceeds a specified threshold. 
    The collected frequency points and associated timestamps are saved in the same location as the original CSV file, 
    adding a '_processed' to the end of the name.

    Parameters
    ----------
    file_path : str
        Path to the CSV file containing pico timestamps in the second column.
    f_s_factor : int, optional
        Resampling frequency factor. The data is resampled at a frequency which is `f_s_factor` times larger 
        than the maximum frequency observed in the data. Default is 4.
    f_c : float, optional
        Cutoff frequency for the Butterworth low-pass filter. Default is 1.25.
    threshold : float, optional
        Minimum frequency difference (in Hz) required to collect a point. Default is 0.1 Hz.

    Returns
    -------
    None
        This function does not return any value. The collected frequency points and timestamps are saved in a csv file.
    '''

    df = pd.read_csv(file_path, names=['pi_timestamps', 'timestamps'])
    df['frequency'] = 1/(df['timestamps'].diff().shift(-1)) * 1e9 # Hz
    df['timediff'] = (df['timestamps'].diff().shift(-1)) / 1e6 # ms
    df = df.ffill() # last row uses frequency and timediff from the previous row

    timestamps, values = list(df.timestamps), list(df.timediff)

    # Timestamps are not uniformly sampled, re-sample with equal spacing at frequency f_s, using linear interpolation
    f_s = f_s_factor*max(df.frequency)
    sampled_timestamps = np.linspace(min(timestamps), max(timestamps), int((max(timestamps)-min(timestamps))/1e9 * f_s))
    interpolation_func = interp1d(timestamps, values, kind='linear')
    interpolated_values = interpolation_func(sampled_timestamps)

    # Filter the sampled signal using a butterworth low-pass filter
    b, a = butter(N=5, Wn=f_c, fs=f_s, btype='low', analog=False)
    filtered_values = filtfilt(b, a, interpolated_values)

    # Convert the filtered time differences (ms) to frequency (Hz)
    filtered_values = [1/x*1000 for x in filtered_values]

    # Collect points where the difference between consecutive frequencies exceeds the threshold
    collected_filtered_values = [filtered_values[0]]
    collected_filtered_times = [sampled_timestamps[0]]
    for i in range(1, len(filtered_values)):
        if abs(filtered_values[i] - collected_filtered_values[-1]) > threshold:
            collected_filtered_values.append(filtered_values[i])
            collected_filtered_times.append(sampled_timestamps[i])

    # Write the results to a csv file in the same location as the original file
    df_output = pd.DataFrame({'time':collected_filtered_times, 'frequency':collected_filtered_values})
    df_output.to_csv(file_path.replace('.csv','_processed.csv'), index=False)

    print(f"Sucessfully reduced the data size {round(len(df)/len(df_output))}-fold")


# ---------------
# EXAMPLE USE
# ---------------

csv_file = os.getcwd() + '/flow_data/beech/downstairs_zone/hall_sensor_2024-07-11_00-38-51.csv'
process_timestamps(csv_file)

df = pd.read_csv(csv_file.replace('.csv','_processed.csv'))
plt.plot(df.time, df.frequency)
plt.xlabel('Time')
plt.ylabel('Frequency [Hz]')
plt.show()
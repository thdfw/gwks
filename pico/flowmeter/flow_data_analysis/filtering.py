import numpy as np
import csv
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

def filter_and_collect(timestamps:list[float|int], csv_path:str, f_s_factor:int=4, f_c:float=1.25, threshold:float=0.1):
    '''
    Filters and collects frequency points from a list of timestamps.

    This function receives a list of timestamps, computes the time difference between consecutive timestamps,
    applies a low-pass Butterworth filter to smooth the time difference data, converts the filtered data to frequency,
    and then collects frequency points where the difference between consecutive frequencies exceeds a specified threshold. 
    The collected frequency points and associated timestamps are saved in a csv file.

    Parameters
    ----------
    timestamps : list[float|int]
        List of timestamps in nanoseconds
    csv_path: str
        Path to the desired csv file where the results will be saved
    f_s_factor : int, optional
        Resampling frequency factor. The data is resampled at a frequency which is `f_s_factor` times larger 
        than the maximum frequency observed in the data. Default is 4.
    f_c : float, optional
        Cutoff frequency for the Butterworth low-pass filter. Default is 1.25.
    threshold : float, optional
        Minimum frequency difference (in Hz) required to collect a point. Default is 0.1 Hz.
    '''

    # Compute the time differences and frequency
    timestamps_diff = [y-x for x,y in zip(timestamps[:-1],timestamps[1:])]
    timestamps_diff = timestamps_diff + [timestamps_diff[-1]]
    timediff = [x/1e6 for x in timestamps_diff] # ms
    frequency = [(1/x)*1e9 for x in timestamps_diff] # Hz

    # Re-sample time with equal spacing at sampling frequency f_s, using linear interpolation
    f_s = f_s_factor*max(frequency)
    sampled_timestamps = np.linspace(min(timestamps), max(timestamps), int((max(timestamps)-min(timestamps))/1e9 * f_s))
    interpolation_func = interp1d(timestamps, timediff, kind='linear')
    interpolated_timediff = interpolation_func(sampled_timestamps)

    # Filter the sampled signal using a butterworth low-pass filter
    b, a = butter(N=5, Wn=f_c, fs=f_s, btype='low', analog=False)
    filtered_timediff = filtfilt(b, a, interpolated_timediff)

    # Convert the filtered time differences (ms) to frequency (Hz)
    filtered_frequency = [1/x*1000 for x in filtered_timediff]

    # Collect points where the difference between consecutive frequencies exceeds the threshold
    collected_frequency = [filtered_frequency[0]]
    collected_timestamps = [sampled_timestamps[0]]
    for i in range(1, len(filtered_frequency)):
        if abs(filtered_frequency[i] - collected_frequency[-1]) > threshold:
            collected_frequency.append(filtered_frequency[i])
            collected_timestamps.append(sampled_timestamps[i])

    # Append the results to a csv file
    with open(csv_path.replace('.csv','_processed.csv'), mode='a', newline='') as file:
        rows = zip(collected_timestamps, collected_frequency)
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Sucessfully reduced the data size {round(len(timestamps)/len(collected_timestamps))}-fold")
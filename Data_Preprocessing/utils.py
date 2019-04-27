import numpy as np

def get_statistics(array):
    mean_val = np.mean(array)
    min_val = np.min(array)
    max_val = np.max(array)
    return mean_val, min_val, max_val

def reject_outliers(data, m=7.):
    # How far is the data from median?
    d = np.abs(data - np.median(data))
    # Scale the deviation by median
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    # Reject outliers
    return data[s < m], s >= m

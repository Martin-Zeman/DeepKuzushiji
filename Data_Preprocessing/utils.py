import numpy as np
import os
import re


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


def get_book_id(image_path):
    if image_path is None:
        return None
    basename = os.path.basename(image_path)
    return re.split('_|-', basename)[0]

def get_image_name(image_path):
    if image_path is None:
        return None
    basename = os.path.basename(image_path)
    return os.path.splitext(basename)[0]

def delete_images(images):
    for image in images:
        try:
            os.remove(image)
        except OSError:
            print(f"Cannot delete {image}!")
    print("Finished deleting images!")

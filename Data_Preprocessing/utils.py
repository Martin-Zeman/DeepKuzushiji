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

def get_corresponding_txt_file_paths(image_paths):
    txt_file_paths = []
    for image_path in image_paths:
        path, _ = os.path.splitext(image_path)
        txt_file_paths.append(path + ".txt")
    return txt_file_paths


def is_fully_within_crop(crop_spans, character_xy, character_dims):
    ret = False
    height_span, width_span = crop_spans
    char_x, char_y = character_xy
    char_height, char_width = character_dims

    fits_on_x_axis = char_x >= width_span[0] and (char_x + char_width) <= width_span[1]
    fits_on_y_axis = char_y >= height_span[0] and (char_y + char_height) <= height_span[1]

    if fits_on_x_axis and fits_on_y_axis:
        ret = True
    return ret

#!/usr/bin/python3.6

from PIL import Image
import argparse
from pathlib import Path
from image_iterator import ImageIterator
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import get_statistics, reject_outliers

def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    parser.add_argument("-i", "--ignore", nargs="*", type=str)
    return parser

def get_aspect_ratios(dir, ignore):
    """Returns a two equally sized numpy arrays. First holds the aspect ratios of all images found recursively in the
    given directory. The second one holds their filenames without the extension."""
    asp_ratios = []
    img_names = []

    images = ImageIterator(dir, ignore)
    for image in images:
        with Image.open(image) as img:
            width, height = img.size
            asp_ratios.append(width/height)
            # img_names.append(os.path.splitext(os.path.basename(image))[0])
            img_names.append(image)
    return np.array(asp_ratios), np.array(img_names)

def plot_aspect_ratio_histogram(aspect_ratios):
    asp_ratios_series = pd.Series(aspect_ratios)
    asp_ratios_series.plot.hist(grid=True, bins=20, rwidth=0.9, color='#607c8e')
    plt.title("Aspect ratio histogram")
    plt.xlabel("Aspect Ratio")
    plt.ylabel("Frequency")
    plt.grid(axis='y', alpha=0.75)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = define_arguments(parser)
    args = parser.parse_args()

    aspect_ratios, image_names = get_aspect_ratios(args.dir, args.ignore)

    mean_val, min_val, max_val = get_statistics(aspect_ratios)
    print(f"Mean = {mean_val}, Min = {min_val}, Max = {max_val}")
    plot_aspect_ratio_histogram(aspect_ratios)

    aspect_ratios_filtered, rejected_indices = reject_outliers(aspect_ratios)

    mean_val, min_val, max_val = get_statistics(aspect_ratios_filtered)
    print(f"Mean = {mean_val}, Min = {min_val}, Max = {max_val}")
    plot_aspect_ratio_histogram(aspect_ratios_filtered)

    # a = image_names[rejected_indices]
    # b = aspect_ratios[rejected_indices]
    # dict = {}
    # for A, B in zip(a, b):
    #     dict[A] = B
    # print(dict)


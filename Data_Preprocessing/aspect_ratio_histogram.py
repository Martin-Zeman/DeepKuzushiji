#!/usr/bin/python3.6

from PIL import Image
import argparse
from pathlib import Path
from image_iterator import ImageIterator
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean


def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    parser.add_argument("-i", "--ignore", nargs="*", type=str)
    return parser

def get_aspect_ratios(dir, ignore):
    """Returns a list of aspect ratios of all images found recursively in the given directory"""
    asp_ratios = []

    images = ImageIterator(dir, ignore)
    for image in images:
        with Image.open(image) as img:
            width, height = img.size
            asp_ratios.append(width/height)
    return asp_ratios

def get_statistics(list):
    mean_val = mean(list)
    min_val = min(list)
    max_val = max(list)

    return mean_val, min_val, max_val

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

    aspect_ratios = get_aspect_ratios(args.dir, args.ignore)
    mean_val, min_val, max_val = get_statistics(aspect_ratios)
    print(f"Mean = {mean_val}, Min = {min_val}, Max = {max_val}")
    plot_aspect_ratio_histogram(aspect_ratios)




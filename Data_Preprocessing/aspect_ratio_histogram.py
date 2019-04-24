#!/usr/bin/python3.6

from PIL import Image
import argparse
from pathlib import Path
from image_iterator import ImageIterator


def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    return parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = define_arguments(parser)
    args = parser.parse_args()

    aspect_ratios = []

    files = ImageIterator(args.dir)
    for f in files:
        print('\t%s' % f)


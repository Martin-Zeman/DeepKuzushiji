#!/usr/bin/python3.6

from aspect_ratios import get_aspect_ratios
import argparse
from pathlib import Path
import numpy as np
from utils import reject_outliers, get_statistics
from distutils import dir_util
import time
from threading import Thread
from csv_editor import erase_references


class TreeCopyThread(Thread):
    def __init__(self, src, dest):
        super(TreeCopyThread, self).__init__()

        self.src = src
        self.dest = dest

    def run(self):
        dir_util.copy_tree(self.src, self.dest)


class ProgressThread(Thread):
    def __init__(self, worker):
        super(ProgressThread, self).__init__()

        self.worker = worker

    def run(self):
        while True:
            if not self.worker.is_alive():
                print("Copying done!")
                return True

            print("Copying ...")
            time.sleep(2.0)

def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    parser.add_argument("-o", "--out", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics_Preprocessed",
                        help="Output path to the root of the preprocessed dataset directory")
    parser.add_argument("-c", "--copy", dest='copy', action='store_true')
    parser.set_defaults(copy=False)
    parser.add_argument("-i", "--ignore", nargs="*", type=str)
    return parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = define_arguments(parser)
    args = parser.parse_args()

    # Make a copy to be processed if needed
    if args.copy:
        copy_thread = TreeCopyThread(str(args.dir), str(args.out))
        progress = ProgressThread(copy_thread)
        copy_thread.start()
        progress.start()
        progress.join()

    aspect_ratios, image_names = get_aspect_ratios(args.out, args.ignore)
    aspect_ratios_filtered, rejected_indices = reject_outliers(aspect_ratios)
    mean_val, _, _ = get_statistics(aspect_ratios_filtered)

    rejected_images_paths = image_names[rejected_indices]
    erase_references(str(args.dir), rejected_images_paths)


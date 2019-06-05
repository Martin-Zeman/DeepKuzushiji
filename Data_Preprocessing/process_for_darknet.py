#!/usr/bin/python3.6

from aspect_ratios import get_aspect_ratios
import argparse
from pathlib import Path
import numpy as np
from utils import reject_outliers, get_statistics, delete_images
from distutils import dir_util
import time
from threading import Thread
from csv_editor import erase_references

from file_iterator import DirectoryIterator


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

def create_class_directory(root_dir):
    """
    Creates a dictionary mapping from a class number 0..n and their respective character codes
    :param root_dir: starting point of the search for all 'characters' subdirectories
    :return:
    """
    class_num_to_char = {}
    dirs = DirectoryIterator(root_dir, must_contain="U+", ignore_list=["images"])
    class_counter = 0
    for dir in dirs:
        if dir not in class_num_to_char.keys():
            class_num_to_char[dir] = class_counter
            class_counter += 1

    return class_num_to_char

def test_train_split():
    None

def save_paths_to_file(path_list, output_path):
    None

def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    parser.add_argument("-o", "--out", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics_Darknet",
                        help="Output path to the root of the preprocessed dataset directory")
    parser.add_argument("-c", "--copy", dest='copy', action='store_true')
    parser.set_defaults(copy=False)
    parser.add_argument("-i", "--ignore", nargs="*", type=str)
    return parser


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = define_arguments(parser)
    args = parser.parse_args()

    # # Make a copy to be processed if needed
    # if args.copy:
    #     copy_thread = TreeCopyThread(str(args.dir), str(args.out))
    #     progress = ProgressThread(copy_thread)
    #     copy_thread.start()
    #     progress.start()
    #     progress.join()
    #
    # aspect_ratios, image_names = get_aspect_ratios(args.out, args.ignore)
    # aspect_ratios_filtered, rejected_indices = reject_outliers(aspect_ratios)
    # mean_val, _, _ = get_statistics(aspect_ratios_filtered)
    #
    # rejected_images_paths = image_names[rejected_indices]
    # erase_references(str(args.out), rejected_images_paths)
    # delete_images(rejected_images_paths)

    classes = create_class_directory(args.dir)
    print(len(classes))


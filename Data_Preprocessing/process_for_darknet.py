#!/usr/bin/python3.6

from aspect_ratios import get_aspect_ratios
import argparse
from pathlib import Path
import numpy as np
from utils import *
from distutils import dir_util
import time
from threading import Thread
from csv_editor import get_bounding_boxes, erase_references
from process_images import process_image_for_darknet
from file_iterator import DirectoryIterator, FileIterator


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

def get_image_paths(root_dir):
    """
    Returns a list of paths to all the images in the root_dir recursively.
    :param root_dir: starting point of the search for all 'characters' subdirectories
    :return: list of image paths under the root_dir
    """
    paths = []
    images = FileIterator(root_dir, ignore_list=["characters"])
    for image in images:
        paths.append(image)
    return paths

def convert_bb_to_relative_numbers(df, image_width, image_height):
    """
    Converts the <absolute_x> <absolute_y> <absolute_width> <absolute_height> of the bounding box from absolute to
    relative numbers <x> <y> <width> <height> as follows:
    <x> = <absolute_x> / <image_width>
    <y> = <absolute_y> / <image_height>
    <width> = <absolute_width> / <image_width>
    <height> = <absolute_height> / <image_height>
    :param df: pandas dataframe for a single image
    :return: converted dataframe
    """
    df.loc[:, "X"] /= image_width
    df.loc[:, "Y"] /= image_height
    df.loc[:, "Width"] /= image_width
    df.loc[:, "Height"] /= image_height
    return df


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

    # Make a copy to be processed if needed
    if args.copy:
        copy_thread = TreeCopyThread(str(args.dir), str(args.out))
        progress = ProgressThread(copy_thread)
        copy_thread.start()
        progress.start()
        progress.join()

    # aspect_ratios, image_names = get_aspect_ratios(args.out, args.ignore)
    # aspect_ratios_filtered, rejected_indices = reject_outliers(aspect_ratios)
    # mean_val, _, _ = get_statistics(aspect_ratios_filtered)
    #
    # rejected_images_paths = image_names[rejected_indices]
    # erase_references(str(args.out), rejected_images_paths)
    # delete_images(rejected_images_paths)

    classes = create_class_directory(args.dir)
    print(len(classes))
    img_paths = get_image_paths(args.dir)
    txt_paths = get_corresponding_txt_file_paths(img_paths)

    counter = 0
    for index, img_path in enumerate(img_paths):
        new_width, new_height = process_image_for_darknet(img_path)
        bb_df = get_bounding_boxes(img_path)
        if counter == 50:
            print(bb_df)
        relative_bb_df = convert_bb_to_relative_numbers(bb_df, new_width, new_height)
        if counter == 50:
            print(relative_bb_df)
        counter += 1


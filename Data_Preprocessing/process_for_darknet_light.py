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
import random

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
    Creates three dictionaries:
    - dictionary mapping from a class number 0..n and their respective character codes.
    - dictionary mapping from character code to its respective class number
    - dictioanry mapping from character code to its frequency of usage
    :param root_dir: starting point of the search for all 'characters' subdirectories
    :return:
    """
    class_num_to_char = {}
    char_to_class_num = {}
    char_to_freq = {}
    dirs = DirectoryIterator(root_dir, must_contain="U+", ignore_list=["images"])
    class_counter = 0
    for dir in dirs:
        if dir not in char_to_class_num.keys():
            char_to_class_num[dir] = class_counter
            char_to_freq[dir] = 1
            class_num_to_char[class_counter] = dir
            class_counter += 1
        else:
            char_to_freq[dir] += 1

    return class_num_to_char, char_to_class_num, char_to_freq


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

def convert_chars_to_classes(df, char_to_class_dict):
    """
    Uses the char_to_class dict to replace the character unicodes in the first column of the dataframe with their
    respective class numbers.
    :param df:
    :param char_to_class_dict:
    :return: converted dataframe
    """
    df["Unicode"].replace(char_to_class_dict, inplace=True)
    is_missing = df.isnull().values.any()
    assert not is_missing, "Fatal Error! Found NaN in the Unicode column of a dataframe!"
    return df

def create_test_and_train_files(img_paths, train_percentage, out_dir):
    """
    Creates the test.txt and train.txt files required by darknet.
    :param img_paths: paths to all the images to be trained/tested on
    :param train_percentage: floating point number between 0 < x < 1.0
    :param out_dir: Path type directory where the train.txt and test.txt are to be created
    :return:
    """
    assert 0 < train_percentage < 1.0, "Invalid train percentage value!"
    train_path = str((out_dir / "train.txt").resolve())
    test_path = str((out_dir / "test.txt").resolve())
    with open(train_path, "w") as f_train:
        with open(test_path, "w") as f_test:
            for img in img_paths:
                belongs_to_train_set = random.uniform(0.0, 1.0) <= train_percentage
                if belongs_to_train_set:
                    f_train.write(img + "\n")
                else:
                    f_test.write(img + "\n")


def create_names_file(char_to_class, out_dir):
    """
    Creates the obj.names file required by Darknet. It contains all the class names one per line.
    :param char_to_class:
    :return:
    """
    names_path = str((out_dir / "obj.names").resolve())
    with open(names_path, "w") as f_names:
        for val in char_to_class.keys():
            f_names.write(val + "\n")


def create_data_file(char_to_class, out_dir):
    """
    Creates the obj.data file required by Darknet.
    :param char_to_class:
    :return:
    """
    data_path = str((out_dir / "obj.data").resolve())
    with open(data_path, "w") as f_data:
        f_data.write(str(len(char_to_class)) + "\n")
        f_data.write("train = train.txt\n")
        f_data.write("valid = test.txt\n")
        f_data.write("names = obj.names\n")
        f_data.write("backup = backup/\n")


def define_arguments(parser):
    parser.add_argument("-d", "--dir", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics",
                        help="Path to the root dataset directory")
    parser.add_argument("-o", "--out", type=Path,
                        default=Path(__file__).absolute().parent.parent / "Datasets/Japanese_Classics_Darknet",
                        help="Output path to the root of the preprocessed dataset directory")
    parser.add_argument("-c", "--copy", dest='copy', action='store_true')
    parser.set_defaults(copy=False)
    parser.add_argument("-i", "--ignore", nargs="*", type=str, default=[])
    return parser

def find_all_imgs_using_character(char):
    None
    #TODO only use this this select a couple of images and delete all the rest.

def sort_characters_by_frequency(char_to_freq):
    None
    # TODO use the char_to_freq output of the create_class_directory


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
    erase_references(str(args.out), rejected_images_paths)
    delete_images(rejected_images_paths)

    _, char_to_class, char_to_freq = create_class_directory(args.out)
    img_paths = get_image_paths(args.out)
    txt_paths = get_corresponding_txt_file_paths(img_paths)

    num_images = len(img_paths)
    for index, img_path in enumerate(img_paths):
        new_width, new_height = process_image_for_darknet(img_path)
        bb_df = get_bounding_boxes(img_path)
        relative_bb_df = convert_bb_to_relative_numbers(bb_df, new_width, new_height)
        relative_bb_df = convert_chars_to_classes(relative_bb_df, char_to_class)
        np.savetxt(txt_paths[index], relative_bb_df.values, fmt="%i %.18e %.18e %.18e %.18e")
        print(f"Processed {index + 1}/{num_images}")
    create_test_and_train_files(img_paths, 0.9, args.out / "cfg")
    create_names_file(char_to_class, args.out / "cfg")
    create_data_file(char_to_class, args.out / "cfg")
    print("Done!")


import pandas as pd
from pandas.errors import ParserError
from utils import get_book_id, get_image_name, is_fully_within_crop
from file_iterator import FileIterator
import os


def erase_references(root_dir, image_paths):
    image_book_ids = [get_book_id(x) for x in image_paths]
    image_names = [get_image_name(x) for x in image_paths]

    files = FileIterator(root_dir, extension=".csv", must_contain="coordinate", ignore_list=["characters", "images"])
    for file in files:
        try:
            df = pd.read_csv(file, encoding='ISO-8859-1')
        except ParserError:
            print(f"Error parsing file {file}. Fix the file manually.")

        # Get rid of Unnamed columns
        column_names = list(df.columns.values)
        columns_to_delete = [x for x in column_names if "Unnamed" in x]
        for column in columns_to_delete:
            df = df.drop(column, axis=1)

        for i, book_id in enumerate(image_book_ids):
            if book_id in file:
                # The image doesn't necessarily have to be referenced if there's no kanji in it
                df = df[df.Image != image_names[i]]
        df.to_csv(file, encoding='ISO-8859-1')
    print(f"Finished deleting references!")

def get_csv_path_from_image_path(image_path):
    # TODO: look if there's a better way to do the joining
    dir = os.path.split(image_path)
    dir_of_csv = dir[0].split("/")[0:-1]
    dir_of_csv = "/".join(dir_of_csv)
    book_id = get_book_id(image_path)
    csv_filename = "".join([book_id, "_coordinate.csv"])
    csv_path = "/".join([dir_of_csv, csv_filename])
    return csv_path


def resize_bbs_in_csv(image_path, multiplier_w, multiplier_h):
    csv_path = get_csv_path_from_image_path(image_path)
    try:
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')
    except ParserError:
        print(f"Fatal Error while parsing file {csv_path}. Bounding boxes not adjusted!")
        return
    image_name = get_image_name(image_path)

    df.loc[df.Image == image_name, "X"] *= multiplier_w
    df.loc[df.Image == image_name, "Y"] *= multiplier_h
    df.loc[df.Image == image_name, "Width"] *= multiplier_w
    df.loc[df.Image == image_name, "Height"] *= multiplier_h

    df.to_csv(csv_path, encoding='ISO-8859-1', index=False)

def replace_images_with_crops_in_csv(image_path_to_crops, crop_to_orig, orig_to_crop):
    for image_path in image_path_to_crops.keys():
        csv_path = get_csv_path_from_image_path(image_path)
        try:
            df = pd.read_csv(csv_path, encoding='ISO-8859-1')
        except ParserError:
            print(f"Fatal Error while parsing file {csv_path}. Original not replaced with crops for {image_path}!")
            return
        image_name = get_image_name(image_path)
        image_data = df.loc[df.Image == image_name, ["Unicode", "X", "Y", "Char ID", "Width", "Height"]]
        df.drop(df.Image == image_name, axis=0)

        crops = image_path_to_crops[image_path]
        for _, row in image_data.iterrows():
            for crop in crops:
                crop_name = crop[-1]
                height_span = crop[1]
                width_span = crop[2]
                # print(f"crop name  =  {crop_name}")
                # print(f"height span = {height_span}")
                # print(f"width span = {width_span}")
                # print(f"Unicode {row['Unicode']} X {row['X']} Y {row['Y']} Width {row['Width']} Height {row['Height']}")
                if is_fully_within_crop((width_span, height_span), (row['X'], row['Y']), (row['Width'], row['Height'])):
                    print(f"Character {row['Char ID']} is within crop {crop_name} where width span = {width_span} height span = {height_span}")
                    break
            else:
                print(f"Character {row['Char ID']} didn't fit anywhere")
                # TODO I need to watch the YOLO videos again to find out if having the same character appear in multiple
                #  crops is a problem. Or alternatively not marking (and thus learning) all the characters in a crop
                #  because I used them in a different crop. Also I need to have a look at the encoding in general again.

import pandas as pd
from pandas.errors import ParserError
from utils import get_book_id, get_image_name
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
    dir = os.path.split(image_path)
    dir_of_csv = dir[0].split("/")[0:-1]
    dir_of_csv = "/".join(dir_of_csv)
    book_id = get_book_id(image_path)
    csv_filename = "".join([book_id, "_coordinate.csv"])
    csv_path = "/".join([dir_of_csv, csv_filename])
    return csv_path


def resize_bbs(image_path, multiplier_w, multiplier_h):
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

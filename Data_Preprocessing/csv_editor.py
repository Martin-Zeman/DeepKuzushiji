import pandas as pd
from pandas.errors import ParserError
from utils import get_book_id, get_image_name
from file_iterator import FileIterator


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



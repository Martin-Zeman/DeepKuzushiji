import pandas as pd
from utils import get_book_id, get_image_name
from file_iterator import FileIterator


def erase_references(root_dir, image_paths):
    image_book_ids = [get_book_id(x) for x in image_paths]
    image_names = [get_image_name(x) for x in image_paths]

    files = FileIterator(root_dir, extension=".csv", must_contain="coordinate", ignore_list=["characters", "images"])
    for file in files:
        for i, book_id in enumerate(image_book_ids):
            if book_id in file:
                print(f"In file {file} I found the book_id={book_id} and am going to erase all references to {image_names[i]}")
                df = pd.read_csv(file, encoding='ISO-8859-1')
                # print(df['Image'][5])



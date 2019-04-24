import os

class ImageIterator:
    """Iterates over all .jpg image paths in a directory subtree specified in the constructor. It navigates in a BFS manner."""

    def __init__(self, root_dir=None):
        self.root_dir = root_dir
        self.current_dir = root_dir

    def __iter__(self):
        if self.root_dir is None:
            raise StopIteration

        for dir_name, subdir_list, file_list in os.walk(self.root_dir):
            for file_name in file_list:
                file_path = os.path.join(self.root_dir, file_name)
                _, file_extension = os.path.splitext(file_path)
                if file_extension != '.jpg':
                    continue
                yield file_path
            for subdir_name in subdir_list:
                yield from ImageIterator(os.path.join(self.root_dir, subdir_name))
        raise StopIteration

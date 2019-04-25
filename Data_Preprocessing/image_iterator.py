import os

class ImageIterator:
    """Iterates over all .jpg image paths in a directory subtree specified in the constructor. It navigates in a BFS manner."""

    def __init__(self, root_dir=None, ignore_list=[]):
        self.root_dir = root_dir
        self.ignore_list = ignore_list

    def __iter__(self):
        if self.root_dir is None:
            raise StopIteration

        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)
            if os.path.isfile(item_path):
                _, file_extension = os.path.splitext(item_path)
                if file_extension != '.jpg':
                    continue
                yield item_path
            if os.path.isdir(item_path):
                if item not in self.ignore_list:
                    yield from ImageIterator(item_path, self.ignore_list)
        raise StopIteration

import os

class FileIterator:
    """Iterates over all files in a directory subtree specified in the constructor. It navigates in a BFS manner.
    @param root_dir - root directory where the search is started
    @param extension - all files expect the ones with this extension will be ignored
    @param must_contain - any file with a basename not containing this will be ignored
    @param ignore_list - list of directory names not to be searched
    """

    def __init__(self, root_dir=None, extension='.jpg', must_contain=None, ignore_list=[]):
        self.root_dir = root_dir
        self.extension = extension
        self.must_contain = must_contain
        self.ignore_list = ignore_list

    def __iter__(self):
        if self.root_dir is None:
            raise StopIteration

        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)
            if os.path.isfile(item_path):
                _, file_extension = os.path.splitext(item_path)
                if file_extension != self.extension:
                    continue
                if self.must_contain is not None and self.must_contain not in os.path.basename(item):
                    continue
                yield item_path
            if os.path.isdir(item_path):
                if item not in self.ignore_list:
                    yield from FileIterator(item_path, self.extension, self.must_contain, self.ignore_list)
        raise StopIteration

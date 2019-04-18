import os


class File(object):
    """
    Convenience class for file objects
    """
    def __init__(self, filepath):
        self.path = filepath
        self.name = os.path.basename(filepath)
        self.size = os.path.getsize(filepath)

        self.id = None
        self.part_numbers = 0
        self.chunk_size = 0

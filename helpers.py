import os
from distutils.dir_util import copy_tree
from shutil import rmtree


# Use this function to copy a file or a folder
def copy_csv(from_path, to_path):
    make_directory(to_path)
    if os.path.isfile(from_path):
        with open(to_path, 'w') as to_file, open(from_path, 'r') as from_file:
            for line in from_file:
                    to_file.write(line)
    elif os.path.isdir(from_path):
        copy_tree(from_path, to_path)
    else:
        raise ValueError("Copy_CSV Error. File either does not exist, or is an unsupported file type")

def compare_csv(file_1, file_2):
    if os.path.isfile(file_1) and os.path.isfile(file_1):
        with open(file_1) as f1, open(file_2) as f2:
            for line1, line2 in zip(f1, f2):
                if line1 != line2:
                    return False
        return True
    else:
        return False

def make_directory(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def remove_directory(path):
    if os.path.exists(path):
        rmtree(path)
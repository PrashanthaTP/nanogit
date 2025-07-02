import os
from nanogit import core

def should_ignore_path(filepath):
    #TODO:; get git directory name from a single location
    return '.ngit' in filepath.split(os.sep)

def write_tree(directory="."):
    with os.scandir(directory) as it:
        for entry in it:
            full = os.path.join(directory,entry.name)
            if should_ignore_path(full):
                print(full)
                continue
            if entry.is_file(follow_symlinks=False):
                print(full)#TODO: update object store
                with open(full,'rb') as f:
                    print(core.hash_object(f.read()))
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

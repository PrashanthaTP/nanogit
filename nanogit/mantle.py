import os

def write_tree(directory="."):
    with os.scandir(directory) as it:
        for entry in it:
            full = os.path.join(directory,entry.name)
            if entry.is_file(follow_symlinks=False):
                print(full)#TODO: update object store
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

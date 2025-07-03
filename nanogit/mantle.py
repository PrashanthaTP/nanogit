import os
from nanogit import core

def should_ignore_path(filepath):
    #TODO:; get git directory name from a single location
    return '.ngit' in filepath.split(os.sep)

def write_tree(directory="."):
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full = os.path.join(directory,entry.name)
            if should_ignore_path(full):
                continue
            if entry.is_file(follow_symlinks=False):
                # print(full)#TODO: update object store
                type_ = 'blob'
                with open(full,'rb') as f:
                    oid = core.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree(full)
            entries.append((entry.name, oid, type_))
    tree = ''.join(f"{type_} {oid} {name}\n" for (name,oid,type_) in entries)
    return core.hash_object(tree.encode(), 'tree')

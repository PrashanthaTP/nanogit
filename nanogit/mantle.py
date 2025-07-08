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


def delete_dir(parent_dir):
    for root,dirs,files in os.walk(parent_dir, topdown=False):
        for file in files:
            file_fullpath = os.path.join(root,file)
            if should_ignore_path(file_fullpath):
                continue
            if os.path.isfile(file_fullpath):
                os.remove(file_fullpath)
        for dir in dirs:
            dir_fullpath = os.path.join(root,dir)
            if should_ignore_path(dir_fullpath):
                continue
            try:
                os.rmdir(dir_fullpath)
            except (FileNotFoundError,OSError) as e:
                continue
            
def iter_tree_entries(oid):
    if not oid:
        return
    tree = core.get_object(oid,expected='tree')
    for line in tree.decode().splitlines():
        type_, item_oid, path = line.split(' ',2)
        yield type_, item_oid, path

def get_paths_dict(oid,base_path):
    d = {}
    for type_, item_oid, path in iter_tree_entries(oid):
        if type_ == 'blob':
            d[item_oid] = os.path.join(base_path,path)
        elif type_ == 'tree':
            d.update(get_paths_dict(item_oid,os.path.join(base_path,path)))
        else:
            assert False, f"Unknown oid type: {type_}"
    return d
            
def read_tree(tree_oid):
    if input(f"Type 'yes' to delete contents of current directory {os.getcwd()} : ").strip()=="yes":
        # for now keeping this check 
        # print("Running delete_dir")
        delete_dir('.')
    for oid, path in get_paths_dict(tree_oid,base_path='.').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(path)
        with open(path,'wb') as f:
            f.write(core.get_object(oid))


def commit(message):
    details = f"tree {write_tree()}\n"
    details += "\n"
    details += f"{message}"

    oid = core.hash_object(details.encode(),type_="commit")
    set_HEAD(oid)
    return oid
    
def set_HEAD(oid):
    with open(os.path.join(core.GIT_DIR,'HEAD'),'w') as f:
        f.write(oid)

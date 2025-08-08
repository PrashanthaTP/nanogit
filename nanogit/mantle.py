import os
import operator
import string
import textwrap
import itertools
from collections import namedtuple,deque

from nanogit import core

RefValue = namedtuple("RefValue",["symbolic","value"])

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
    parentHEAD = get_ref(core.HEAD_REF).value
    if parentHEAD:
        details += f"parent {parentHEAD}\n"
    details += "\n"
    details += f"{message}"

    oid = core.hash_object(details.encode(),type_="commit")
    set_ref(core.HEAD_REF,RefValue(symbolic=False,value=oid))
    return oid

Commit = namedtuple("Commit",["tree","parent","message"])
def get_commit(oid):
    commit = core.get_object(oid,expected="commit")
    lines = iter(commit.decode().splitlines())
    parent = None
    tree = None
    # for line in lines:
    for line in itertools.takewhile(operator.truth,lines):
        key,value = line.split(' ',1)
        if key=='tree':
            tree = value
        elif key=='parent':
            parent = value
        else:
            assert False, f"Unknown key while getting commit info: {key}"
            break
    message = "\n".join(lines)
    return Commit(tree=tree,parent=parent,message=message)

def log(oid=None):
    # oid = get_oid(oid)#!TODO is it needed? what if a 'named' ref passed?
    for oid in iter_commits_and_parents({oid}):
        commit = get_commit(oid)
        log_msg = f"commit {oid}\n"
        log_msg += textwrap.indent(commit.message,"    ")
        log_msg += "\n"
        print(log_msg)

def checkout(oid):
    commit = get_commit(oid)
    read_tree(commit.tree)
    set_ref(core.HEAD_REF,RefValue(symbolic=False,value=oid))

def create_tag(name,oid):
    set_ref(os.path.join(core.TAG_DIR,name),RefValue(symbolic=False,value=oid))

def get_oid(ref_name):
    if ref_name == "@":
        ref_name = core.HEAD_REF
    refs_to_try = [
        ref_name,
        os.path.join("refs",ref_name),
        os.path.join(core.TAG_DIR,ref_name),
        os.path.join("refs","heads",ref_name)
        ]
    for ref in refs_to_try:
        oid = get_ref(ref,deref=False).value
        if oid:
            return oid
    # check if ref_name is SHA1
    isOid = all(letter in string.hexdigits for letter in ref_name)
    if len(ref_name)==core.OID_LEN and isOid:
        return ref_name
    assert False, f"Unknown ref name {ref_name}"

def iter_refs(deref=True):
    refs = [core.HEAD_REF]
    for root,_,files in os.walk(os.path.join(core.GIT_DIR,core.REF_DIR)):
        root = os.path.relpath(root,start=core.GIT_DIR)
        refs.extend(os.path.join(root,ref) for ref in files)
    
    for refname in refs:
        yield refname,get_ref(refname,deref=deref   )
        
def iter_commits_and_parents(oids):
    oids = deque(oids)
    visited = set()
    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid
        
        commit = get_commit(oid)
        oids.appendleft(commit.parent)
        
def create_branch(branch_name,oid):
    set_ref(os.path.join("refs","heads",branch_name),RefValue(symbolic=False,value=oid))

def get_ref(ref,deref=True)->RefValue:
    return __get_ref_internal(ref,deref)[1]

def __get_ref_internal(ref,deref):
    #always returns symbolic = False
    ref_path = os.path.join(core.GIT_DIR,ref)
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path,'r') as f:
            value = f.read().strip()
    symbolic = bool(value) and value.startswith("ref:")
    if symbolic:
        value = value.split(":",1)[1].strip()
        if deref:
            return __get_ref_internal(value,deref=True)
    return ref, RefValue(symbolic=symbolic,value=value)

def set_ref(ref,oid: RefValue,deref=True):
    assert not oid.symbolic
    ref = __get_ref_internal(ref,deref  )[0]
    ref_path = os.path.join(core.GIT_DIR,ref)   
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path,'w') as f:
        f.write(oid.value)

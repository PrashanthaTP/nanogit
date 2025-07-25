import argparse
import sys

from nanogit.utils import get_logger
from nanogit import core,mantle

logger = get_logger()
type_oid = mantle.get_oid

def init(args):
    logger.info("init called")
    core.init()

def hash_object(args):
    with open(args.file,'rb') as file:
        print(core.hash_object(file.read()))

def cat_file(args):
    #sys.stdout is buffered but sys.stdout.buffer isn't
    sys.stdout.flush()
    sys.stdout.buffer.write(core.get_object(oid=args.object,expected=None))
    
def write_tree(args):
    print(mantle.write_tree(args.directory))

def read_tree(args):
    mantle.read_tree(args.tree)

def commit(args):
    print(mantle.commit(args.message))

def log(args):
    mantle.log(args.oid)

def checkout(args):
    mantle.checkout(args.oid)

def tag(args):
    mantle.create_tag(args.name, args.oid)

def k(args):
    dot = 'digraph commits {\n'
    oids = set()
    for refname, ref in mantle.iter_refs():
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref}"\n'
        oids.add(ref)
        # print(f"{refname} : {ref}")
    
    for oid in mantle.iter_commits_and_parents(oids):
        commit = mantle.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        # print(oid)
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'
            # print("Parent: ",commit.parent)
    dot += '}'
    print(dot)
    print("Note: View in http://www.webgraphviz.com/")

def parse_args():
    parser = argparse.ArgumentParser(prog="Nano Git",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commands = parser.add_subparsers(dest="command")

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")
    
    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object",type=type_oid)

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)
    write_tree_parser.add_argument("directory")

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree",type=type_oid)

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m","--message",required=True)

    log_parser = commands.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("oid",type=type_oid,default="@",nargs="?")#optional argument

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("oid",type=type_oid)
    
    tag_parser = commands.add_parser("tag")
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument("name")
    tag_parser.add_argument("oid",type=type_oid,default="@",nargs="?")

    k_parser = commands.add_parser("k")
    k_parser.set_defaults(func=k)
    
    return parser.parse_args()

def main():
    print("You are running Nanogit")
    args = parse_args()
    args.func(args)

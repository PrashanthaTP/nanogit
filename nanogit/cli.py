import argparse
import sys

from nanogit.utils import get_logger
from nanogit import core,mantle

logger = get_logger()

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
    cat_file_parser.add_argument("object")

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)
    write_tree_parser.add_argument("directory")

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree")

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m","--message",required=True)

    return parser.parse_args()

def main():
    print("You are running Nanogit")
    args = parse_args()
    args.func(args)

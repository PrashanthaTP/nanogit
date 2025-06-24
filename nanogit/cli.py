import argparse

from nanogit.utils import get_logger
from nanogit import core

logger = get_logger()

def init(args):
    logger.info("init called")
    core.init()

def hash_object(args):
    with open(args.file,'rb') as file:
        print(core.hash_object(file.read()))

def parse_args():
    parser = argparse.ArgumentParser(prog="Nano Git",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commands = parser.add_subparsers(dest="command")

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")
    
    return parser.parse_args()

def main():
    print("You are running Nanogit")
    args = parse_args()
    args.func(args)

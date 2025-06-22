import argparse
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s | %(name)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')

def init(args):
    logger.info("init called")
    
def parse_args():
    parser = argparse.ArgumentParser(prog="Nano Git",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    commands = parser.add_subparsers(dest="command")

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    return parser.parse_args()

def main():
    print("You are running Nanogit")
    args = parse_args()
    args.func(args)

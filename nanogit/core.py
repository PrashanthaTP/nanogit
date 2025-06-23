import os

from nanogit.utils import get_logger
logger = get_logger()

GIT_DIR=".ngit"

#TODO: create git direcotry in specified directory - take it as an argument
def init():
    os.makedirs(GIT_DIR,exist_ok=True)
    logger.info("Initialized empty .ngit repository in %s"%(os.getcwd()))

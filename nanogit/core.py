import os
import hashlib

from nanogit.utils import get_logger
logger = get_logger()

GIT_DIR=".ngit"
OBJECT_DIR=os.path.join(GIT_DIR,"objects")
#TODO: create git direcotry in specified directory - take it as an argument
def init():
    os.makedirs(GIT_DIR,exist_ok=True)
    os.makedirs(OBJECT_DIR,exist_ok=True)
    logger.info("Initialized empty .ngit repository in %s"%(os.getcwd()))

def hash_object(data):
    oid = hashlib.sha1(data).hexdigest()
    with open(os.path.join(OBJECT_DIR,oid),'wb') as file:
        file.write(data)
    return oid

def get_object(oid):
    with open(os.path.join(OBJECT_DIR,oid),'rb') as file:
        return file.read()

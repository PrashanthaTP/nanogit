import os
import hashlib

from nanogit.utils import get_logger
logger = get_logger()

GIT_DIR=".ngit"
OBJECT_DIR=os.path.join(GIT_DIR,"objects")
HEAD_REF="HEAD"
HEAD_FILE=os.path.join(GIT_DIR,HEAD_REF)
TAG_DIR=os.path.join('refs','tags')
REF_DIR="refs"
OID_LEN=40

#TODO: create git direcotry in specified directory - take it as an argument
def init():
    os.makedirs(GIT_DIR,exist_ok=True)
    os.makedirs(OBJECT_DIR,exist_ok=True)
    logger.info("Initialized empty .ngit repository in %s"%(os.getcwd()))

def hash_object(data, type_="blob"):
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(obj).hexdigest()
    with open(os.path.join(OBJECT_DIR,oid),'wb') as file:
        file.write(obj)
    return oid

def get_object(oid,expected=None):
    obj = ""
    with open(os.path.join(OBJECT_DIR,oid),'rb') as file:
        obj = file.read()
    type_,_,content = obj.partition(b'\x00')
    type_ = type_.decode()
    if expected is not None:
        #Exception handling?
        assert type_ == expected, f"Expected {expected}, got {type_}"

    return content

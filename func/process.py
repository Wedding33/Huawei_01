from base.manager import *
from .utils import print_function_time, flush

# @print_function_time
def preprocess(manager: Manager):
    del_list = [input().split() for _ in range(args.M)]
    write_list = [input().split() for _ in range(args.M)]
    read_list = [input().split() for _ in range(args.M)]
    # TODO: preprocess data
    print("OK")
    flush()

def del_postprocess():
    pass

def write_postprocess():
    pass

def read_postprocess():
    pass
from base.manager import *
from .utils import print_function_time, flush

# @print_function_time
def preprocess(manager: Manager):
    del_list = [list(map(int, input().split())) for _ in range(args.M)]
    write_list = [list(map(int, input().split())) for _ in range(args.M)]
    read_list = [[0] + list(map(int, input().split())) for _ in range(args.M)]

    net_write_list = [
        [write_list[i][j] - del_list[i][j] for j in range(args.num_slice)] for i in range(args.M)]
    # obj_num_list = [
    #     [sum(net_write_list[i][:j]) for i in range(args.M)] for j in range(args.num_slice + 1)]     # num_slice * M
    obj_num_list = [
        [sum(net_write_list[i][:j]) for j in range(args.num_slice + 1)] for i in range(args.M)]     # M * (num_slice + 1)
    # read_list = [list(ls) for ls in zip(*read_list)]

    manager.register_prob(obj_num_list, read_list)
    
    
    
    print("OK")
    flush()

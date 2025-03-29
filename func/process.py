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

    num_sections = len(PROPORTION)
    sec_obj_num_list = [[0] * (args.num_slice + 1) for _ in range(num_sections)]
    sec_read_list = [[0] * (args.num_slice + 1) for _ in range(num_sections)]
    for i in range(args.M):
        for sec_id in SECTION_MAP[i + 1]:
            for j in range(args.num_slice + 1):
                sec_obj_num_list[sec_id - 1][j] += obj_num_list[i][j]
                sec_read_list[sec_id - 1][j] += read_list[i][j]
    manager.register_prob(obj_num_list, read_list, sec_obj_num_list, sec_read_list)
    
    
    
    print("OK")
    flush()

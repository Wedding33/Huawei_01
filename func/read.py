from base.manager import *
from .utils import *

def scan_and_read_disk(manager: Manager):
    finished_reqests = []
    path = [None] * args.N
    @print_function_time
    def scan_and_read():
        for i, disk in enumerate(manager.disks):
            path[i], reqs = disk.scan_and_read()
            finished_reqests.extend(reqs)
    scan_and_read()
    return path, finished_reqests

# @print_function_time
def read_action(manager: Manager):
    # NOTE: register requests
    nRead = int(input())
    requests = []
    req_ids = []
    obj_ids = []
    @print_function_time
    def input_request():
        for _ in range(1, nRead + 1):
            read_input = input().split()
            req_ids.append(int(read_input[0]))
            obj_ids.append(int(read_input[1]))
    @print_function_time
    def register_request():
        for i in range(nRead):
            object = manager.get_object(obj_ids[i])
            requests.append(object.register_request(req_ids[i]))
    input_request()
    register_request()
    manager.register_requests(requests)

    if any(info in DEBUG_INFO for info in ["object", "disk"]) and DEBUG_TIMESTAMP in [None, timer.time()]:
        manager.print_debug_info()

    # NOTE: process requests
    info, finish_list = scan_and_read_disk(manager)

    # @print_function_time
    def print_info(info):
        info = '\n'.join([str(p) for p in info] + [str(len(finish_list))])
        if len(finish_list) > 0:
            info += '\n'.join([''] + [str(i) for i in finish_list])
        print(info)
    print_info(info)


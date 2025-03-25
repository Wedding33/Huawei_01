from base.manager import *
from .utils import *

# @print_function_time
def scan_and_read_disk(manager: Manager):
    finished_reqests = []
    for disk in manager.disks:
        path, reqs = disk.scan_and_read()
        # finished_reqests.extend(reqs)
        print("#")
    return finished_reqests

@print_function_time
def read_action(manager: Manager):
    # NOTE: register requests
    nRead = int(input())
    for _ in range(1, nRead + 1):
        read_input = input().split()
        req_id = int(read_input[0])
        object = manager.get_object(int(read_input[1]))
        object.register_request(req_id)

    if any(info in DEBUG_INFO for info in ["object", "disk"]):
        manager.print_debug_info()

    # NOTE: process requests
    finish_list = scan_and_read_disk(manager)

    print(len(finish_list))
    if len(finish_list) > 0:
        print('\n'.join([str(i) for i in finish_list]))


from base.manager import *
from .utils import *

def select_disk_demo(object: Object):
    return [(object.id + j) % args.N + 1 for j in range(1, REP_NUM + 1)]

def select_unit_demo(disk: Disk, size: int):
    units = []
    for i in range(1, 1 + args.V):
        if disk.unit_is_empty(i):
            units.append(disk.get_unit(i))
        if len(units) == size:
            break
    assert len(units) == size
    return units

# @print_function_time
def select_disk_unit(manager: Manager, object: Object):
    disks = [manager.get_disk(disk_id) for disk_id in select_disk_demo(object)]
    units_list = [select_unit(disk, object.size) for disk in disks]
    return units_list    # REP_NUM * size

def select_unit(disk: Disk, size):
    units = disk.find_n_empty_units(size)
    assert (units is not None) and (len(units) == size)
    return units

# @print_function_time
def get_write_info(units_list: List[List[Unit]]):
    info = f"{units_list[0][0].object_id}\n"
    for units in units_list:
        info += f"{units[0].disk_id}"
        for unit in units:
            info += f" {unit.id}"
        info += "\n"
    return info.strip()

# @print_function_time
def write_action(manager: Manager):  
    info = []  
    n_write = int(input())
    for _ in range(n_write):
        write_input = input().split()
        object_id = int(write_input[0])
        size = int(write_input[1])
        tag = int(write_input[2])
        object = Object(object_id, size, tag)

        # TODO: design a function to select disk and unit
        units_list = select_disk_unit(manager, object)

        object.register_units(units_list)
        manager.register_object_and_disk(object, units_list)
        
        if any(info in DEBUG_INFO for info in ["object", "disk"]):
            manager.print_debug_info()
            
        info.append(get_write_info(units_list))

    if n_write > 0:    
        print('\n'.join(info))
    flush()
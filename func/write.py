from base.manager import *
from .utils import *

def select_disk(manager: Manager, object: Object):
    return [(object.id + j) % args.N + 1 for j in range(1, REP_NUM + 1)]
def select_unit(disk: Disk, size, tag, rep_id):
    units = disk.get_section(tag, rep_id).find_n_empty_units(size)
    assert (units is not None) and (len(units) == size)
    return units

# @print_function_time
def select_disk_unit_v3(manager: Manager, object: Object):
    disks = [manager.get_disk(disk_id) for disk_id in select_disk(manager, object)]
    units_list = [select_unit(disk, object.size, object.tag, i) for i, disk in enumerate(disks)]
    return units_list    # REP_NUM * size

def select_disk_unit(manager: Manager, object: Object):
    units_list = []
    count = 0
    disk_id_list = []
    for rep_id in range(REP_NUM):
        for i in range(args.N):
            disk_id = (manager.tag_count[object.tag] + i) % args.N + 1
            if disk_id in disk_id_list:
                continue
            units = manager.get_disk(disk_id).get_section(object.tag, rep_id).find_n_empty_units(object.size)
            if units is not None:
                count += 1
                disk_id_list.append(disk_id)
                units_list.append(units)
                manager.tag_count[object.tag] += 1
                break
        if count < rep_id + 1:
            for i in range(args.N):
                disk_id = (manager.tag_count[object.tag] + i) % args.N + 1
                if disk_id in disk_id_list:
                    continue
                for sec in manager.get_disk(disk_id).get_sections():
                    units = sec.find_n_empty_units(object.size)
                    if units is not None:
                        count += 1
                        disk_id_list.append(disk_id)
                        units_list.append(units)
                        manager.tag_count[object.tag] += 1
                        manager.overflow_count += object.size
                        break
                if count == rep_id + 1: break
            assert count == rep_id + 1, [[unit.id for unit in units] for units in units_list]
    assert all(len(units) == object.size for units in units_list), [[unit.id for unit in units] for units in units_list]
    return units_list    # REP_NUM * size


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

        units_list = select_disk_unit(manager, object)
        # units_list = select_disk_unit_v3(manager, object)

        object.register_units(units_list)
        manager.register_object_and_disk(object, units_list)
        
        if any(info in DEBUG_INFO for info in ["object", "disk"]) and DEBUG_TIMESTAMP in [None, timer.time()]:
            manager.print_debug_info()
            
        info.append(get_write_info(units_list))

    if n_write > 0:    
        print('\n'.join(info))
    flush()
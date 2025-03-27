from .config import *
from .object import *
from .disk import *
from .prob import *
from typing import List
from queue import Queue


class Manager:
    def __init__(self):
        # NOTE: start from 1
        self.disks: List[Disk] = [Disk(i, args.V, args.G) for i in range(1, args.N + 1)]
        self.objects: Dict[int, Object] = {}
        self.work_queue: Queue = Queue(maxsize=EXTRA_TIME)

        # FIXME: add effective requests queue
        self.timestamp = 0
        self.tag_count = {i: 0 for i in range(1, args.M + 1)}


        # auxiliary data
    def get_disk(self, i: int) -> Disk:
        return self.disks[i - 1]
    
    def get_object(self, i: int):
        # return self.objects[i - 1]
        return self.objects[i]
    
    def pop_object(self, i: int):
        # obj = self.objects[i - 1]
        # self.objects[i - 1] = None
        # return obj
        return self.objects.pop(i)
    
    def recycle_units(self, obj: Object):
        disk_unit_dict = obj.get_recycle_pos()
        for disk_id, unit_id_size_dict in disk_unit_dict.items():
            for unit_id, size in unit_id_size_dict.items():
                self.get_disk(disk_id).get_section(obj.tag).recycle_unit(unit_id, size)

    # @print_function_time
    def register_requests(self, requests: List[Request]):
        self.work_queue.put(requests)
    
    # @print_function_time
    def clear_timeout_requests(self):
        if self.work_queue.full():
            timeout_requests: List[Request] = self.work_queue.get()
            for req in timeout_requests:
                if req.is_on_going():
                    self.get_object(req.object_id).move_timeout_request(req)
    
    def register_object_and_disk(self, object: Object, unit_list: List[List[Unit]]):
        self.objects[object.id] = object
        for units in unit_list:
            disk = self.get_disk(units[0].disk_id)
            disk.register_max_written_pos(units)

    def register_prob(self, obj_num_list, read_list):
        prob = Prob(obj_num_list, read_list)
        for disk in self.disks:
            disk.register_prob(prob)


    def print_debug_info(self):
        list2str = lambda x: '[' + ', '.join(str(item) for item in x) + ']'
        
        import json
        if "object" in DEBUG_INFO:
            object_info = {
                'time': timer.time(),
                'objects': {
                    f'id: {obj.id}': {
                        'size': obj.size, 
                        'tag': obj.tag, 
                        'requests': obj.get_ongoing_requests(id_only=True), 
                        'record': {
                            k: list2str(obj.record[k])
                            for k in obj.record if k != 'disk'
                        }, 
                        'disk': {
                            k: list2str(obj.record['disk'][k])
                            for k in obj.record['disk']
                        }
                    }
                    for obj in self.objects.values() if obj is not None
                }
            }
            with open(OBJECT_OUTPUT_PATH, 'w') as file:
                print(json.dumps(object_info, indent=4), file=file)

        if "disk" in DEBUG_INFO:
            disk_info = {
                'time': timer.time(), 
                'disks': {
                    f'id: {disk.id}': {
                        'point': f'{disk.point}',
                        'max_written_pos': f'{disk.max_written_pos}',
                        'pre_token': f'{disk.pre_token}',
                        'tokens_left': f'{disk.tokens_left}',
                        'unit_info': [
                            f'uid: {unit.id}, obj_id: {unit.object_id}, req_ids: {list2str(unit.block.requests.keys())}'
                            for unit in disk.data if unit.is_requested()
                        ],
                        
                    } for disk in self.disks
                }
            }

            with open(DISK_OUTPUT_PATH, 'w') as file:
                print(json.dumps(disk_info, indent=4), file=file)

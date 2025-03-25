from .config import *
from .object import *
from .disk import *
from typing import List
from queue import Queue
    
class Manager:
    def __init__(self):
        # NOTE: start from 1
        self.disks: List[Disk] = [Disk(i, args.V, args.G) for i in range(1, args.N + 1)]
        self.objects: List[Object] = [None] * MAX_OBJECT_NUM

        # FIXME: add effective requests queue
        self.timestamp = 0
        self.prob = None    # asssigned by 'preprocess', length is num_slices

        # auxiliary data
    def get_disk(self, i: int):
        return self.disks[i - 1]
    
    def get_object(self, i: int):
        return self.objects[i - 1]
    
    def pop_object(self, i: int):
        obj = self.objects[i - 1]
        self.objects[i - 1] = None
        return obj
    
    def register_object(self, object: Object):
        self.objects[object.id - 1] = object

    def print_debug_info(self):
        list2str = lambda x: '[' + ', '.join(str(item) for item in x) + ']'
        object_info = {
            'time': timer.time(),
            'objects': {
                f'id: {obj.id}': {
                    'size': obj.size, 
                    'tag': obj.tag, 
                    'requests': obj.get_ongoing_requests(), 
                    'record': {
                        k: list2str(obj.record[k])
                        for k in obj.record if k != 'disk'
                    }, 
                    'disk': {
                        k: list2str(obj.record['disk'][k])
                        for k in obj.record['disk']
                    }
                }
                for obj in self.objects if obj is not None
            }
        }

        disk_info = {
            'time': timer.time(), 
            'disks': {
                f'id: {disk.id}': {
                    'point': f'{disk.point}',
                    'pre_token': f'{disk.pre_token}',
                    'tokens_left': f'{disk.tokens_left}',
                    'continuous': f'{disk.continuously_read}',
                    'unit_info': [
                        f'uid: {unit.id}, obj_id: {unit.object_id}, req_ids: {list2str(unit.block.requests.keys())}'
                        for unit in disk.data if unit.is_requested()
                    ],
                    
                } for disk in self.disks
            }
        }

        import json
        with open(OBJECT_OUTPUT_PATH, 'w') as file:
            print(json.dumps(object_info, indent=4), file=file)

        with open(DISK_OUTPUT_PATH, 'w') as file:
            print(json.dumps(disk_info, indent=4), file=file)
"""
    # for prob-based algorithms
    def init_prob(self, del_list, write_list, read_list):
        lengths = [len(ls) for ls in (del_list + write_list + read_list)]
        assert all([length == lengths[0] for length in lengths])
        num_tags = [len(lols) for lols in [del_list, write_list, read_list]]
        assert all([num_tag == num_tags[0] for num_tag in num_tags])
        num_slices, num_tags = lengths[0], num_tags[0]
        del_slices = list(zip(*del_list))
        write_slices = list(zip(*write_list))
        read_slices = list(zip(*read_list))
        # self.prob = [PhaseProb(i, num_tags, ds, ws, rs) for i, (ds, ws, rs) in enumerate(zip(del_slices, write_slices, read_slices))]

    def find_slice(self, timestamp):
        return timestamp // FRE_PER_SLICING

    def get_tags_count(self):
        pass
"""
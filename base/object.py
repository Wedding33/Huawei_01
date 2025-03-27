from .config import *
from typing import List, Dict
from func.utils import print_function_time

class Object:
    ...

class Request:
    def __init__(self, idx, object: Object):
        self.id = idx
        self.object_id = object.id
        self.object = object
        self.size_to_read = object.size
        self.timestamp = timer.time()
        self.on_going = True

    def read(self):
        self.size_to_read -= 1
        if self.is_done():
            self.on_going = False
    
    def is_done(self):
        return self.size_to_read == 0
    
    def is_on_going(self):
        return self.on_going
    
    def deactivate(self):
        self.on_going = False
    
    def is_out_of_time(self):
        return timer.time() - self.timestamp >= EXTRA_TIME
    

class Block:
    def __init__(self, object_id):
        # self.id = idx
        self.object_id = object_id
        self.requests: Dict[int, 'Request'] = {}
        self.units: List[Unit] = []

    def is_requested(self):
        for req in self.requests.values():
            if not req.is_out_of_time():
                return True
        return False
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    # FIXME
    def read(self):
        finished_list = []
        for idx in list(self.requests.keys()):
            req = self.requests.pop(idx)
            req.read()
            if req.is_done():
                finished_list.append(idx)
        return finished_list

class Unit:
    def __init__(self, idx, disk_id):
        self.id = idx
        self.disk_id = disk_id
        self.object_id = 0  # object id
        self.block: Block = None

    def is_empty(self):
        return self.block is None
    
    def is_requested(self):
        if self.block is None:
            return False
        return self.block.is_requested()

    def register_block(self, block: Block):
        self.object_id = block.object_id
        self.block = block
        self.block.add_unit(self)

    def read(self) -> List[int]:
        """ return finished request id list """
        assert self.block is not None, f"timestamp {timer.time()}, disk_id: {self.disk_id}, unit_id: {self.id}, object_id: {self.object_id}"
        return self.block.read()

class Object:
    def __init__(self, object_id, size, tag):
        self.id = object_id
        self.size = size
        self.blocks = [Block(object_id) for _ in range(size)]
        self.tag = tag
        self.timeout_requests = []

        self.record: Dict[str, List] = {'write': [], 'delete': [], 'read': [], 'disk': {}}

    def register_units(self, units_list: List[List[Unit]]):
        # NOTE: units_list: REP_NUM * size
        for units in units_list:
            self.record['disk'][units[0].disk_id] = [unit.id for unit in units]
            for i, unit in enumerate(units):
                unit.register_block(self.blocks[i])
        self.record['write'].append(timer.time())

    def unregister_units(self):
        for block in self.blocks:
            for unit in block.units:
                unit.block = None
                unit.object_id = 0

    def get_ongoing_requests(self, id_only=False):
        # NOTE: get ongoing requests
        request = set()
        for block in self.blocks:
            request = request.union(block.requests.keys() if id_only else block.requests.values())
        return list(request)
    
    def move_timeout_request(self, request: Request):
        for block in self.blocks:
            block.requests.pop(request.id, None)
        self.timeout_requests.append(request.id)

    def delete(self):   
        # NOTE: get ongoing requests
        requests = self.get_ongoing_requests()
        for req in requests:
            req.deactivate()
        # NOTE: unregister units
        self.unregister_units()
        self.record['delete'].append(timer.time())
        return [req.id for req in requests] + self.timeout_requests
    
    def get_recycle_pos(self) -> Dict[int, Dict[int, int]]:
        recycle_pos: Dict[int, Dict[int, int]] = dict()
        for block in self.blocks:
            for unit in block.units:
                if unit.disk_id not in recycle_pos:
                    recycle_pos[unit.disk_id] = dict()
                next_unit = False
                for start_pos in recycle_pos[unit.disk_id]:
                    if start_pos + recycle_pos[unit.disk_id][start_pos] == unit.id:
                        recycle_pos[unit.disk_id][start_pos] += 1
                        next_unit = True
                        break
                if next_unit: continue
                recycle_pos[unit.disk_id][unit.id] = 1
        return recycle_pos

    def register_request(self, request_id):
        # NOTE: register request
        request = Request(request_id, self)
        for block in self.blocks:
            block.requests[request_id] = request
        self.record['read'].append(timer.time())
        return request

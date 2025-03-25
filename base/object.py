from .config import *
from typing import List, Dict

class Request:
    def __init__(self, idx, size):
        self.id = idx
        self.size_to_read = size
        self.timestamp = timer.time()

    def read(self):
        self.size_to_read -= 1
    
    def is_done(self):
        return self.size_to_read == 0

class Block:
    def __init__(self, object_id):
        # self.id = idx
        self.object_id = object_id
        self.requests: Dict[int, 'Request'] = {}
        self.units: List[Unit] = []

    def is_requested(self):
        return len(self.requests) > 0
    
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

    def read(self):
        return self.block.read()

class Object:
    def __init__(self, object_id, size, tag):
        self.id = object_id
        self.size = size
        self.blocks = [Block(object_id) for _ in range(size)]
        self.tag = tag

        self.record = {'write': [], 'delete': [], 'read': [], 'disk': {}}

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

    def get_ongoing_requests(self):
        # NOTE: get ongoing requests
        request = set()
        for block in self.blocks:
            request = request.union(block.requests.keys())
        return list(request)

    def delete(self):   
        # NOTE: get ongoing requests
        request = self.get_ongoing_requests()
        # NOTE: unregister units
        self.unregister_units()
        self.record['delete'].append(timer.time())
        return list(request)


    def register_request(self, request_id):
        # NOTE: register request
        request = Request(request_id, self.size)
        for block in self.blocks:
            block.requests[request_id] = request
        self.record['read'].append(timer.time())

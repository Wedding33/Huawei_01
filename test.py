import timeit
from typing import Dict, List

class Request:
    def __init__(self, idx, obj_id, size):
        self.id = idx
        self.object_id = obj_id
        self.size_to_read = size
        self.on_going = True


class Block:
    def __init__(self, object_id):
        # self.id = idx
        self.object_id = object_id
        self.requests: Dict[int, 'Request'] = {}
        self.units: List[Unit] = []


class Unit:
    def __init__(self, idx, disk_id):
        self.id = idx
        self.disk_id = disk_id
        self.object_id = 0  # object id
        self.block: Block = None


    def register_block(self, block: Block):
        self.object_id = block.object_id
        self.block = block
        self.block.units.append(self)


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
            for i, unit in enumerate(units):
                unit.register_block(self.blocks[i])
    
    def register_request(self, request_id):
        # NOTE: register request
        request = Request(request_id, self.id, self.size)
        for block in self.blocks:
            block.requests[request_id] = request
        return request


NUM = 3000
objs = [Object(i, i, i) for i in range(NUM)]
req_ids = [i for i in range(NUM)]
requests = [None] * NUM
def register_requests1():
    for i in range(NUM):
        requests[i] = objs[i].register_request(req_ids[i])
t1 = timeit.timeit(register_requests1, number=10)
print(f"register_requests1: {t1 / 10} 秒")

def register_requests2():
    for i in range(NUM):
        request = requests[i] = Request(req_ids[i], objs[i].id, objs[i].size)
        for block in objs[i].blocks:
            block.requests[req_ids[i]] = request

t2 = timeit.timeit(register_requests2, number=10)
print(f"register_requests2: {t2 / 10} 秒")

from .config import *
from .object import *
from typing import List
from math import ceil
from func.utils import print_function_time

class Disk:
    def __init__(self, idx, disk_size, max_token):
        self.id = idx
        self.disk_size = disk_size
        self.data: List[Unit] = [Unit(i + 1, idx) for i in range(disk_size)]
        self.point = 1
        self.pre_token = None    # token for last operation
        self.max_token  = max_token  # max token for each phase
        self.tokens_left = 0  # tokens left for current phase
        self.continuously_read = False
        # self.mode = 'scan'

    def get_unit(self, i: int):
        return self.data[i - 1]

    def unit_is_empty(self, i: int):
        return self.data[i - 1].is_empty()
    
    def unit_is_requested(self, i: int):
        return self.data[i - 1].is_requested()
    
    def can_jump(self):
        return self.tokens_left == self.max_token
    
    def move_forward(self, distance):
        self.point = (self.point + distance - 1) % len(self.data) + 1

    def register_object(self, object: Object):
        for block in object.blocks:
            for unit in self.data:
                unit.register_block(block)
    
    # FIXME: TOOOOO SLOW
    @print_function_time
    def move_to_readable_block(self):
        # FIXME: note that empty units can be read to keep continuously
        for i in range(self.disk_size):  # FIXME: too large
            unit_id = (i + self.point - 1) % self.disk_size + 1
            if self.unit_is_requested(unit_id):
                if i > 0:
                    self.continuously_read = False  # NOTE: stop reading
                    if i > self.tokens_left:
                        if self.can_jump():
                            # NOTE: jump to the requested block
                            self.move_forward(i)
                            move_info = f'j {self.point}'
                        else:
                            # NOTE: move 'tokens_left' steps forward
                            self.move_forward(self.tokens_left)
                            move_info = 'p' * self.tokens_left
                        self.tokens_left = 0
                        return move_info
                    else:
                        # NOTE: move 'i' steps forward
                        self.move_forward(i)
                        self.tokens_left -= i
                        return 'p' * i
                else:
                    # NOTE: can read the requested block immediately
                    return '' 
        return None

    @print_function_time
    def read_once(self):
        # NOTE: read the requested block
        tokens = max(16, ceil(self.pre_token * 0.8)) if self.continuously_read else 64
        if tokens > self.tokens_left:
            # NOTE: tokens are not enough for reading this block
            self.tokens_left = 0        # end this round (FIXME: consider time value and choose whether pass this block or not)
            return '', []
        else:
            self.tokens_left -= tokens  # read this block
            self.pre_token = tokens
            finished_list = self.get_unit(self.point).read()
            self.move_forward(1)
            self.continuously_read = True
            return 'r', finished_list
    
    @print_function_time
    def scan_and_read(self):
        # reset tokens at the beginning of each round
        self.tokens_left = self.max_token

        total_path = ''
        finished_list = []

        return total_path, finished_list

        while self.tokens_left > 0:
            # NOTE: find a readable block
            path = self.move_to_readable_block()
            if path is not None:
                total_path += path
                if self.unit_is_requested(self.point):
                    read_path, finished = self.read_once()
                    total_path += read_path
                    finished_list.extend(finished)
            else:
                # NOTE: no readable block
                break

        if not total_path.startswith('j'):
            total_path += '#'
            
        return total_path, finished_list
            

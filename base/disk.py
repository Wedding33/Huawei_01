from .config import *
from .object import *
from typing import List
from math import ceil
from func.utils import print_function_time

# TODO
class Sector:   # disk sector for picking valuable blocks
    pass

class SortList(list):
    def append_ascending(self, item):
        left, right = 0, len(self) - 1
        while left <= right:
            mid = (left + right) // 2
            if self[mid] == item:
                left = right = mid
                break
            elif self[mid] < item:
                left = mid + 1
            else:
                right = mid - 1
        self.insert(left, item)


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
        self.max_written_pos = 0

        self.max_obj_size = 5
        self.delete_record = {s: SortList() for s in range(1, self.max_obj_size + 1)}
        # self.mode = 'scan'

    def register_max_written_pos(self, units: List[Unit]):
        for unit in units:
            self.max_written_pos = max(self.max_written_pos, unit.id)

    def get_unit(self, i: int):
        return self.data[i - 1]

    def unit_is_empty(self, i: int):
        return self.data[i - 1].is_empty()
    
    def unit_is_requested(self, i: int):
        return self.data[i - 1].is_requested()
    
    def can_jump(self):
        return self.tokens_left == self.max_token
    
    def move_forward(self, distance):
        if distance != 0:
            self.continuously_read = False
        self.point = (self.point + distance - 1) % len(self.data) + 1

    def move_to(self, unit_id):
        if self.point != unit_id:
            self.continuously_read = False
        self.point = unit_id

    def recycle_unit(self, unit_id, size):
        if size > self.max_obj_size:
            for s in range(self.max_obj_size + 1, size + 1):
                self.delete_record[s] = []
            self.max_obj_size = size
        self.delete_record[size].append_ascending(unit_id)

    def reuse_n_units(self, n, separate=False):
        if not separate:
            for size in range(n, self.max_obj_size + 1):  # FIXME: consider the case that size > 5 (NOTE: the size is not too large)
                if len(self.delete_record[size]) > 0:
                    start_pos = self.delete_record[size].pop(0)
                    units = [self.get_unit(i) for i in range(start_pos, start_pos + n)]
                    if size != n:
                        self.delete_record[size - n].append_ascending(start_pos + n)
                    return units
        else:
            unit_size = []
            sizes = {s: len(self.delete_record[s]) for s in self.delete_record.keys() if (s < n) and len(self.delete_record[s]) > 0}
            while n > 0:
                max_size = max(sizes.keys())
                sizes[max_size] -= 1
                if sizes[max_size] == 0:
                    sizes.pop(max_size)
                unit_size.append(max_size)
                n -= max_size
                if (sizes == {}) or (min(sizes.keys() > n)):
                    return None
            units = []
            for size in unit_size:  # FIXME: consider the case that size > 5 (NOTE: the size is not too large)
                units.extend(self.reuse_n_units(size, separate=False))
            return units
        
    def find_n_empty_units(self, n):
        units = self.reuse_n_units(n, separate=False)
        if units is not None:
            return units
        if self.max_written_pos + n <= self.disk_size:
            start_pos = self.max_written_pos + 1
            units = [self.get_unit(i) for i in range(start_pos, start_pos + n)]
            return units
        return self.reuse_n_units(n, separate=True)

        
    def register_object(self, object: Object):
        for block in object.blocks:
            for unit in self.data:
                unit.register_block(block)
    
    # @print_function_time
    def find_next_readable_block(self):
        for i in range(self.max_written_pos):  # FIXME: too large, consider binary search or hash table to speed up the search process. (NOTE: the max_written_pos is not too large)
            unit_id = (i + self.point - 1) % self.max_written_pos + 1
            if self.unit_is_requested(unit_id):
                return unit_id
        return None
    
    # FIXME: try to use 'r' instead of 'p'
    # @print_function_time
    def move_to_readable_block(self):
        if self.point <= self.max_written_pos:
            for i in range(min(self.max_written_pos - self.point, self.tokens_left) + 1):
                # NOTE: i < self.tokens_left, which means that 'p' is readable
                unit_id = (i + self.point - 1) % self.max_written_pos + 1
                if self.unit_is_requested(unit_id): # found
                    self.move_to(unit_id)
                    self.tokens_left -= i
                    return 'p' * i
        # NOTE: if 'point' is out of range or no readable block, jump (or move as many as possible)
        # FIXME: jump to other places
        if self.can_jump() and self.point != 1:  # jump to the beginning
            self.tokens_left = 0
            self.move_to(1)
            return 'j 1'
        else:  # move as many as possible
            path = 'p' * self.tokens_left
            self.move_forward(self.tokens_left)
            self.tokens_left = 0
            return path

    # @print_function_time
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
    
    def scan_and_read(self):
        # reset tokens at the beginning of each round
        self.tokens_left = self.max_token

        total_path = ''
        finished_list = []
        if self.max_written_pos > 0:
            while self.tokens_left > 0:
                # NOTE: find a readable block
                path = self.move_to_readable_block()
                total_path += path
                while self.unit_is_requested(self.point) and self.tokens_left > 0:
                    read_path, finished = self.read_once()
                    total_path += read_path
                    finished_list.extend(finished)

        if not total_path.startswith('j'):
            total_path += '#'
            
        return total_path, finished_list
            

class DiskReader:
    def __init__(self, disk: Disk):
        self.point = disk.point
        self.max_token = disk.max_token
        self.pre_token = disk.pre_token

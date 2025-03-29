from .config import *
from .section import *
from .prob import Prob
from .path import read_instead_of_pass, cal_read_tokens
from typing import List
from math import floor
from func.utils import print_function_time

class Disk:
    def __init__(self, idx, disk_size, max_token):
        self.id = idx
        self.disk_size = disk_size
        self.sections_start_pos = [0] * len(PROPORTION)
        self.sections_size = [0] * len(PROPORTION)
        pos = 1
        for i in range(len(PROPORTION)):
            size = floor(disk_size * PROPORTION[i])
            self.sections_start_pos[i] = pos
            self.sections_size[i] = size
            pos += size
        self.sections_size[-1] = disk_size - sum(self.sections_size[:-1])
        # FIXME:FIXME: section id
        self.data: List[Unit] = [Unit(i + 1, idx) for i in range(disk_size)]
        self.sections: List[Section] = [Section(i + 1, pos, size, self.get_unit(pos, size)) for i, (pos, size) in enumerate(zip(self.sections_start_pos, self.sections_size))]

        self.point = 1
        self.pre_token = None    # token for last operation
        self.max_token  = max_token  # max token for each phase
        # self.max_read = max_token // 16
        self.tokens_left = 0  # tokens left for current phase
        self.max_written_pos = 0
        self.max_obj_size = 5

        self.prob = None
        # self.mode = 'scan'

    def get_section(self, tag: int, rep_id: int) -> Section: 
        return self.sections[SECTION_MAP[tag][rep_id] - 1]
    
    def get_section_by_sec_id(self, sec_id: int) -> Section:
        return self.sections[sec_id - 1]
    
    def get_sections(self) -> List[Section]:
        return self.sections
    
    def get_section_by_uid(self, uid: int) -> Section: 
        i = 0
        while i < len(self.sections_start_pos) and self.sections_start_pos[i] <= uid:
            i += 1
        return self.sections[i - 1]

    def register_max_written_pos(self, units: List[Unit]):
        section = self.get_section_by_uid(units[0].id)
        section.register_max_written_pos(units)
        for unit in units:
            self.max_written_pos = max(self.max_written_pos, unit.id)

    def limited_idx(self, i: int):
        return (i - 1) % self.disk_size + 1
    def maxpos_limited_idx(self, i: int):
        return (i - 1) % self.max_written_pos + 1

    def get_unit(self, i: int, size=1):
        return self.data[(i - 1): (i - 1 + size)] if size > 1 else self.data[i - 1]

    def unit_is_empty(self, i: int):
        return self.data[i - 1].is_empty()
    
    def unit_is_requested(self, i: int):
        return self.data[i - 1].is_requested()
    
    def continuously_read(self):
        return self.pre_token is not None
    
    def can_jump(self):
        return self.tokens_left == self.max_token
    
    def move_forward(self, distance, mode='pass', pre_token=None):
        if distance != 0:
            self.pre_token = (None if mode == 'pass' else pre_token)
        self.point = self.limited_idx(self.point + distance)
        
    def read_forward(self, distance, pre_token):
        if distance > 0:
            self.pre_token = pre_token
        finished_list = []
        for i in range(distance):
            finished_list.extend(self.get_unit(self.limited_idx(self.point + i)).read())
        self.point = self.limited_idx(self.point + distance)
        return finished_list

    def jump_to(self, unit_id):
        if self.point != unit_id:
            self.pre_token = None
            self.point = unit_id

    def register_prob(self, prob: Prob):
        self.prob = prob
        
    def register_object(self, object: Object):
        for block in object.blocks:
            for unit in self.data:
                unit.register_block(block)
    
    def find_next_requested(self, max_step: int):
        for i in range(max_step + 1):
            unit_id = self.limited_idx(self.point + i)
            if self.unit_is_requested(unit_id): # found
                n_request = 1
                while self.unit_is_requested(self.limited_idx(unit_id + n_request)):
                    n_request += 1
                return unit_id, i, n_request
        return None, None, None
    
    # @print_function_time
    def move_to_readable_block(self):
        if self.point <= self.max_written_pos:
            unit_id, n_pass, n_read = self.find_next_requested(min(self.max_written_pos - self.point, self.tokens_left, self.max_token // SEARCH_DEVISION))
            if "others" in DEBUG_INFO and DEBUG_TIMESTAMP in [None, timer.time()]:
                with open(OTHER_OUTPUT_PATH, 'a') as f:
                    print(f"[DEBUG] in move_to_readable_block: disk {self.id}: unit_id: {unit_id}, n_pass: {n_pass}, n_read: {n_read}, tokens_left: {self.tokens_left}", file=f)
            if unit_id is not None:     # NOTE: i.e., n_read > 0
                if n_pass > 0 and n_pass <= MAX_READ_INSTEAD and self.continuously_read() and read_instead_of_pass(self.pre_token, n_pass, n_read):
                    tokens_used, pre_token, n_pass_success = cal_read_tokens(self.pre_token, n_pass, max_token=self.tokens_left)
                    self.tokens_left -= tokens_used
                    if "others" in DEBUG_INFO:
                        with open(OTHER_OUTPUT_PATH, 'a') as f:
                            print(f"[DEBUG] in move_to_readable_block: disk {self.id} read {n_pass_success} (of {n_pass}) blocks instead of pass blocks ({n_read} reads behind), using {tokens_used} tokens and the pre-token is {pre_token} (self.pre_token={self.pre_token}). There is {self.tokens_left} tokens left.", file=f)
                    self.move_forward(n_pass_success, mode='read', pre_token=pre_token)
                    if n_pass_success < n_pass:
                        # tokens is not enough
                        self.tokens_left = 0
                        n_read = 0
                    return 'r' * n_pass_success, n_read
                else:
                    self.tokens_left -= n_pass
                    self.jump_to(unit_id)
                    return 'p' * n_pass, n_read
                
        # NOTE: if 'point' is out of range or no readable block, jump (or move as many as possible)
        # FIXME: jump to other places
        if self.can_jump() and self.point != 1:  # jump to the beginning
            self.tokens_left = 0
            # FIXME:FIXME
            pos = self.get_section_by_sec_id(timer.get_section_id()).start_pos
            # pos = 1
            # pos = self.get_section(self.prob.choose_tag()).start_pos
            # pos = self.get_section_by_sec_id(self.prob.choose_section()).start_pos
            self.jump_to(pos)
            return f'j {pos}', 0
        else:
            if (self.point + self.tokens_left) < self.max_written_pos:  # move as many as possible
                path = 'p' * self.tokens_left
                self.move_forward(self.tokens_left)
            else:
                path = ''
            self.tokens_left = 0
            return path, 0

    def try_read(self, n_read):
        # NOTE: read the requested block
        # FIXME: optimize
        n_read_origin = n_read
        tokens, pre_token, n_read = cal_read_tokens(self.pre_token, n_read, max_token=self.tokens_left)
        if "others" in DEBUG_INFO and DEBUG_TIMESTAMP in [None, timer.time()]:
            with open(OTHER_OUTPUT_PATH, 'a') as f:
                print(f"[DEBUG] in try_read: disk {self.id}: n_read_origin: {n_read_origin}, n_read: {n_read}, self.pre_token: {self.pre_token}, pre_token: {pre_token}, tokens: {tokens}, tokens_left: {self.tokens_left}", file=f)
        if n_read == 0:     # NOTE: curr unit is requested but has no tokens left
            self.tokens_left = 0
            return '', []
        if n_read_origin > n_read:
            self.tokens_left = 0  # read next time
        else:
            self.tokens_left -= tokens
        finished_list = self.read_forward(n_read, pre_token)
        return 'r' * n_read, finished_list
    
    def scan_and_read(self):
        # reset tokens at the beginning of each round
        self.tokens_left = self.max_token

        total_path = ''
        finished_list = []
        if self.max_written_pos > 0:
            while self.tokens_left > 0:
                # NOTE: find a readable block
                path, n_read = self.move_to_readable_block()
                total_path += path
                if n_read > 0:
                    read_path, finished = self.try_read(n_read)
                    total_path += read_path
                    finished_list.extend(finished)

        if not total_path.startswith('j'):
            total_path += '#'
            
        return total_path, finished_list
            
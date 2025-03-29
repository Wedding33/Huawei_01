## NOTE: FIXED AND PRELOADED CONFIGS
from typing import List, Dict
FRE_PER_SLICING: int = 1800
MAX_DISK_NUM: int = (10 + 1)
MAX_DISK_SIZE: int = (16384 + 1)
MAX_REQUEST_NUM: int = (30000000 + 1)
MAX_OBJECT_NUM: int = (100000 + 1)
REP_NUM: int = 3
EXTRA_TIME: int = 105

REQUEST_ABANDON_THRESHOLD: int = 10
MAX_READ_INSTEAD: int = 0
SEARCH_DEVISION: int = 10
MAX_OBJECT_SIZE: int = 5
# FIXME:FIXME
# PROPORTION: List[float] = [i for i in [0.24, 0.19, 0.20, 0.11, 0.13, 0.13]]
PROPORTION: List[float] = [0.0500, 0.1625, 0.1583, 0.1196, 0.1520, 0.2754, 0.0800]
# PROPORTION = [1.]
SECTION_MAP: Dict[int, int] = {}
# section_id_map: Dict[int, List[int]] = {
#     1: [1, 15, 16],
#     2: [2, 3, 5],
#     3: [6, 7, 8],
#     4: [12, 13],
#     5: [9, 10, 11],
#     6: [4, 14],
# }
# for i in range(1, 7):
#     SECTION_MAP = {**SECTION_MAP, **{j: i for j in section_id_map[i]}}

SECTION_MAP = {
    1: [1, 3, 5],
    2: [2, 6, 7],
    3: [2, 4, 7],
    4: [1, 6, 7],
    5: [2, 3, 5],
    6: [2, 2, 6],
    7: [2, 2, 3],
    8: [4, 6, 6],
    9: [5, 6, 7],
    10: [4, 5, 6],
    11: [2, 5, 6],
    12: [3, 3, 6],
    13: [4, 6, 6],
    14: [3, 5, 6],
    15: [2, 3, 6],
    16: [4, 6, 7]
}


DEBUG_INFO: List[str] = []
# DEBUG_INFO = ["others"]
# DEBUG_INFO = ["disk", "object"]
# DEBUG_INFO = ["disk", "object", "others"]
DEBUG_TIMESTAMP: int = None
# DEBUG_TIMESTAMP = 3
OBJECT_OUTPUT_PATH: str = "./output/object_info.txt"
DISK_OUTPUT_PATH: str = "./output/disk_info.txt"
OTHER_OUTPUT_PATH: str = "./output/others.txt"

TIME_MONITOR: bool = False
# TIME_MONITOR = False
TIME_MONITOR_PATH: str = "./output/time.txt"

# TODO
MULTIPROCESSING: bool = False

class Config:
    def __init__(self):
        self.T: int = 0
        self.M: int = 0
        self.N: int = 0
        self.V: int = 0
        self.G: int = 0
        self.num_slice: int = 0

    def initialize(self, user_input):
        self.T = int(user_input[0])     # {T + EXTRA_TIME} timestamps, [1, 86400]
        self.M = int(user_input[1])     # {M} tags, [1, 16]
        self.N = int(user_input[2])     # {N} disks, [3, 10]
        self.V = int(user_input[3])     # {V} units, [1, 16384]
        self.G = int(user_input[4])     # {G} tokens, [64, 1000]
        self.num_slice = self.T // FRE_PER_SLICING + (1 if self.T % FRE_PER_SLICING != 0 else 0)
    

args = Config()

## NOTE: STEPLY UPDATED TIMESTAMP
class Timer:
    def __init__(self):
        self.timestamp: int = 0
        self.section_timestamp_start = [0, 5, 12, 18, 22, 30, 40]

    
    def time(self):
        return self.timestamp
    
    def time_phase(self):
        return self.timestamp / FRE_PER_SLICING
    
    def set_time(self, time):
        self.timestamp = int(time)

    def get_section_id(self):
        idx = self.timestamp / FRE_PER_SLICING
        sec_id = 1
        while sec_id < len(self.section_timestamp_start) and self.section_timestamp_start[sec_id] <= idx:
            sec_id += 1
        return sec_id
        
        


timer = Timer()

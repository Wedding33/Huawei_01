## NOTE: FIXED AND PRELOADED CONFIGS
FRE_PER_SLICING = 1800
MAX_DISK_NUM = (10 + 1)
MAX_DISK_SIZE = (16384 + 1)
MAX_REQUEST_NUM = (30000000 + 1)
MAX_OBJECT_NUM = (100000 + 1)
REP_NUM = 3
EXTRA_TIME = 105

REQUEST_ABANDON_THRESHOLD = 10
MAX_READ_INSTEAD = 0
SEARCH_DEVISION = 10
MAX_OBJECT_SIZE = 5
# FIXME:FIXME
PROPORTION = [i for i in [0.24, 0.19, 0.20, 0.11, 0.13, 0.13]]
# PROPORTION = [1.]
SECTION_MAP = {}
section_id_map = {
    1: [1, 15, 16],
    2: [2, 3, 5],
    3: [6, 7, 8],
    4: [12, 13],
    5: [9, 10, 11],
    6: [4, 14],
}
for i in range(1, 7):
    SECTION_MAP = {**SECTION_MAP, **{j: i for j in section_id_map[i]}}
# FIXME:FIXME
# SECTION_MAP = {i: 1 for i in range(1, 17)}

DEBUG_INFO = []
# DEBUG_INFO = ["others"]
# DEBUG_INFO = ["disk", "object"]
# DEBUG_INFO = ["disk", "object", "others"]
DEBUG_TIMESTAMP = None
# DEBUG_TIMESTAMP = 3
OBJECT_OUTPUT_PATH = "./output/object_info.txt"
DISK_OUTPUT_PATH = "./output/disk_info.txt"
OTHER_OUTPUT_PATH = "./output/others.txt"

TIME_MONITOR = False
TIME_MONITOR_PATH = "./output/time.txt"

# TODO
MULTIPROCESSING = False

class Config:
    def __init__(self):
        self.T = 0
        self.M = 0
        self.N = 0
        self.V = 0
        self.G = 0
        self.num_slice = 0

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
        self.timestamp = 0
        self.section_order = [6, 3, 3, 2, 1, 5, 2, 5, 4, 4]

    
    def time(self):
        return self.timestamp
    
    def time_phase(self):
        return self.timestamp / FRE_PER_SLICING
    
    def set_time(self, time):
        self.timestamp = int(time)

    def get_section_id(self):
        return self.section_order[self.timestamp // (FRE_PER_SLICING * 5)]


timer = Timer()

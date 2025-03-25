## NOTE: FIXED AND PRELOADED CONFIGS
FRE_PER_SLICING = 1800
MAX_DISK_NUM = (10 + 1)
MAX_DISK_SIZE = (16384 + 1)
MAX_REQUEST_NUM = (30000000 + 1)
MAX_OBJECT_NUM = (100000 + 1)
REP_NUM = 3
EXTRA_TIME = 105

REQUEST_ABANDON_THRESHOLD = 10

# DEBUG_INFO = []
DEBUG_INFO = ["others"]
# DEBUG_INFO = ["disk", "object", "others"]
DEBUG_TIMESTAMP = None
OBJECT_OUTPUT_PATH = "./output/object_info.txt"
DISK_OUTPUT_PATH = "./output/disk_info.txt"
OTHER_OUTPUT_PATH = "./output/others.txt"

TIME_MONITOR = True
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
    

args = Config()

## NOTE: STEPLY UPDATED TIMESTAMP
class Timer:
    def __init__(self):
        self.timestamp = 0
    
    def time(self):
        return self.timestamp
    
    def set_time(self, time):
        self.timestamp = int(time)

timer = Timer()

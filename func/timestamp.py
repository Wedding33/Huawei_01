from base.config import *
from base.manager import Manager
from .utils import *

if "others" in DEBUG_INFO:
    import psutil
    process = psutil.Process()

# @print_function_time
def timestamp_action(manager: Manager):
    timestamp = int(input().split()[1])
    timer.set_time(timestamp)   # for debug
    print(f"TIMESTAMP {timestamp}")
    flush()

    manager.clear_timeout_requests()
    
    if "others" in DEBUG_INFO and DEBUG_TIMESTAMP in [None, timer.time()]:
        with open(OTHER_OUTPUT_PATH, 'a') as f:
            f.write(f"------ TIMESTAMP {timestamp} ------\n")
            f.write(f"Memory used: {process.memory_info().rss / 1024**3:.4f} GB\n")
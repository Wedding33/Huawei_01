from func.timestamp import *
from func.delete import *
from func.write import *
from func.read import *
from func.process import *


if __name__ == '__main__':
    if "others" in DEBUG_INFO:
        with open(OTHER_OUTPUT_PATH, 'w') as f:
            pass
    if TIME_MONITOR:
        with open(TIME_MONITOR_PATH, 'w') as f:
            pass
        
    # initialize args (T, M, N, V, G)
    user_input = input().split()
    args.initialize(user_input)
    manager = Manager()

    # preprocess
    preprocess(manager)


    # main loop
    for item in range(1, args.T + EXTRA_TIME + 1):
        timestamp_action(manager)
        delete_action(manager)
        write_action(manager)
        read_action(manager)

        if DEBUG_TIMESTAMP is not None:
            assert timer.time() != DEBUG_TIMESTAMP
        


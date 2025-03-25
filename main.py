import sys
from func.delete import *
from func.write import *
from func.read import *
from func.process import *

@print_function_time
def timestamp_action():
    timestamp = int(input().split()[1])
    timer.set_time(timestamp)   # for debug
    print(f"TIMESTAMP {timestamp}")
    sys.stdout.flush()

    if DEBUG:
        with open(OTHER_OUTPUT_PATH, 'a') as f:
            f.write(f"------ TIMESTAMP {timestamp} ------\n")


if __name__ == '__main__':
    if DEBUG:
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
        timestamp_action()
        delete_action(manager)
        write_action(manager)
        read_action(manager)

        if DEBUG:
            manager.print_debug_info()
            if DEBUG_TIMESTAMP is not None:
                assert timer.time() != DEBUG_TIMESTAMP
        


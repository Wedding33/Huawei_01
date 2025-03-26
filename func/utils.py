import sys
from base.config import TIME_MONITOR, TIME_MONITOR_PATH, EXTRA_TIME
from time import perf_counter as realtime

TIME0 = realtime() * 1000
def get_realtime():
    global TIME0
    return realtime() * 1000 - TIME0

def print_next(message):
    print(f"{message}", end="")

def flush():
    sys.stdout.flush()

def score_func(x, size):
    if x >= EXTRA_TIME:
        return 0
    f_x = (-5e-3 * x + 1) if x <= 10 else (-1e-2 * x + 1.05)
    g_size = (size + 1) * 0.5
    return f_x * g_size

def value_per_size(size):
    return (size + 1) * 0.5 / size

def print_function_time(func):
    def wrapper(*args, **kwargs):
        start_time = get_realtime()
        result = func(*args, **kwargs)
        end_time = get_realtime()
        execution_time = end_time - start_time
        if TIME_MONITOR:
            with open(TIME_MONITOR_PATH, 'a') as f:
                print(f"Function {func.__name__} executed in {execution_time:.2f} ms.", file=f)
        return result
    return wrapper

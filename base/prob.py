import random
from .config import args, timer

def linear(arr, t):
    length = len(arr)
    assert t >= 0
    
    lower_index = int(t)
    if lower_index >= length - 1:
        return arr[-1]
    upper_index = lower_index + 1

    fractional_part = t - lower_index

    # y = y0 + (y1 - y0) * fractional_part
    return arr[lower_index] + (arr[upper_index] - arr[lower_index]) * fractional_part


class Prob:
    def __init__(self, obj_num_list, read_list):
        # NOTE: both are (M * (num_slice + 1))
        self.obj_num_list = obj_num_list
        self.read_list = read_list

    # TODO:FIXME: maintain a req & obj counts list
    def choose_tag(self):
        # TODO: FIXME: consider object size
        t = timer.time_phase()
        obj_nums = [linear(obj_num_t, t) for obj_num_t in self.obj_num_list]
        req_nums = [linear(req_num_t, t) for req_num_t in self.read_list]

        ratios = [req_num / obj_num for req_num, obj_num in zip(req_nums, obj_nums)]
        ratios = [ratio / sum(ratios) for ratio in ratios]
        return random.choices(list(range(1, args.M + 1)), weights=ratios)[0]


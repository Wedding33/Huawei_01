from base.manager import *
from .utils import *


@print_function_time
def delete_action(manager: Manager):
    n_delete = int(input())
    delete_list = [int(input()) for _ in range(n_delete)]
    abort_list = []
    for object_id in delete_list:
        object = manager.pop_object(object_id)
        assert object is not None
        abort_list.extend(object.delete())
    abort_num = len(abort_list)
        
    print(f"{abort_num}")
    if abort_num > 0:
        print('\n'.join([str(n) for n in abort_list]))
    flush()
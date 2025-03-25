from base.manager import *
from .utils import *





current_request = 0
current_phase = 0
def process_requests_demo(manager, request_id):
    global current_request
    global current_phase

    if current_request == 0 and request_id > 0:
        current_request = request_id
    if current_request == 0:
        for i in range(1, args.N + 1):
            print("#")
        print("0")
    else:
        current_phase += 1
        objectId = manager.requests[current_request].object_id
        for i in range(1, args.N + 1):
            # find the disk that stores the 1st replica
            if (i == manager.objects[objectId].replica[1]) and manager.objects[objectId].available:
                if current_phase % 2 == 1:  # jump to the 1st unit
                    print(f"j {manager.objects[objectId].unit[1][int(current_phase / 2 + 1)]}")
                else:  # read the unit
                    print("r#")
            else:
                print("#")
        if (current_phase == manager.objects[objectId].size * 2) and manager.objects[objectId].available:      # finish reading
            if not manager.objects[objectId].available:
                print("0")
            else:
                print(f"1\n{current_request}")
                manager.requests[current_request].finish()
            current_request = 0
            current_phase = 0
        else:
            if not manager.objects[objectId].available:
                current_request = 0
                current_phase = 0
            print("0")
    flush()

def read_action_demo(manager):
    # load requests
    request_id = 0
    nRead = int(input())
    for i in range(1, nRead + 1):
        read_input = input().split()
        request_id = int(read_input[0])
        objectId = int(read_input[1])
    
        manager.requests[request_id].object_id = objectId
        manager.requests[request_id].prev_id = manager.objects[objectId].last_req
        manager.objects[objectId].last_req = request_id
        manager.requests[request_id].status = 'waiting'
    
    # process requests
    global current_request
    global current_phase

    if current_request == 0 and nRead > 0:
        current_request = request_id
    if current_request == 0:
        for i in range(1, args.N + 1):
            print("#")
        print("0")
    else:
        current_phase += 1
        objectId = manager.requests[current_request].object_id
        for i in range(1, args.N + 1):
            # find the disk that stores the 1st replica
            if (i == manager.objects[objectId].replica[1]) and manager.objects[objectId].available:
                if current_phase % 2 == 1:  # jump to the 1st unit
                    print(f"j {manager.objects[objectId].unit[1][int(current_phase / 2 + 1)]}")
                else:  # read the unit
                    print("r#")
            else:
                print("#")
        if (current_phase == manager.objects[objectId].size * 2) and manager.objects[objectId].available:      # finish reading
            if not manager.objects[objectId].available:
                print("0")
            else:
                print(f"1\n{current_request}")
                manager.requests[current_request].finish()
            current_request = 0
            current_phase = 0
        else:
            if not manager.objects[objectId].available:
                current_request = 0
                current_phase = 0
            print("0")
    flush()
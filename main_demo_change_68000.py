# ---------- 系统常量定义 ---------- 
import sys
import math

# 存储系统参数
FRE_PER_SLICING = 1800            # 时间片频率
MAX_DISK_NUM = (10 + 1)          # 最大磁盘数量（包含索引偏移）
MAX_DISK_SIZE = (16384 + 1)       # 单盘最大容量（包含索引偏移）
MAX_REQUEST_NUM = (30000000 + 1)  # 最大请求数量
MAX_OBJECT_NUM = (100000 + 1)     # 最大对象数量
REP_NUM = 3                      # 每个对象的副本数
EXTRA_TIME = 105                  # 额外运行时间片

# ---------- 存储系统数据结构 ----------
disk = [[0 for _ in range(MAX_DISK_SIZE)] for _ in range(MAX_DISK_NUM)]  # 磁盘存储空间（二维数组）
disk_point = [1 for _ in range(MAX_DISK_NUM)]  # 磁盘当前写入位置指针
disk_pre_token = [64 for _ in range(MAX_DISK_NUM)]  # 磁盘上一次处理的请求ID
_id = [0 for _ in range(MAX_OBJECT_NUM)]       # 临时ID存储数组
pending_reads = []  # 每个元素是字典：{"request_id":..., "object_id":..., "phases":{副本j: 当前阶段}, "write_counts":{副本j: 已写入块数}}

# 请求状态跟踪
current_request = 0   # 当前处理的请求ID
current_phase = 1    # 当前请求处理阶段

# ---------- 对象存储结构 ----------
class Object:
    def __init__(self):
        self.replica = [0 for _ in range(REP_NUM + 1)]  # 副本所在的磁盘ID（索引从1开始）
        self.unit = [[] for _ in range(REP_NUM + 1)]    # 每个副本在磁盘中的存储位置 
        self.size = 0               # 对象大小
        self.lastRequestPoint = 0   # 最后关联的请求ID
        self.isDelete = False       # 删除标记
        self.haveWriteNum = 0      # 写入标记

# 请求追踪数据结构
req_object_ids = [0] * MAX_REQUEST_NUM  # 请求对应的对象ID
req_prev_ids = [0] * MAX_REQUEST_NUM     # 前驱请求ID（用于构建请求链）
req_is_dones = [False] * MAX_REQUEST_NUM # 请求完成状态

objects = [Object() for _ in range(MAX_OBJECT_NUM)]  # 对象实例数组

# ---------- 核心功能函数 ----------
def do_object_delete(object_unit, disk_unit, size):
    """执行对象删除操作（实际是将存储位置置零）"""
    for i in range(1, size + 1):
        disk_unit[object_unit[i]] = 0

def timestamp_action():
    """处理时间戳指令"""
    timestamp = input().split()[1]
    print(f"TIMESTAMP {timestamp}")
    sys.stdout.flush()

def delete_action():
    """处理删除指令（包含事务回滚逻辑）"""
    # 主要功能：
    # 1. 统计需要中止的请求
    # 2. 执行实际删除操作
    # 3. 更新对象删除状态
    n_delete = int(input())
    abortNum = 0
    for i in range(1, n_delete + 1):
        _id[i] = int(input())
    for i in range(1, n_delete + 1):
        delete_id = _id[i]
        currentId = objects[delete_id].lastRequestPoint
        while currentId != 0:
            if not req_is_dones[currentId]:
                abortNum += 1
            currentId = req_prev_ids[currentId]

    print(f"{abortNum}")
    for i in range(n_delete + 1):
        delete_id = _id[i]
        currentId = objects[delete_id].lastRequestPoint
        while currentId != 0:
            if not req_is_dones[currentId]:
                print(f"{currentId}")
            currentId = req_prev_ids[currentId]
        for j in range(1, REP_NUM + 1):
            do_object_delete(objects[delete_id].unit[j], disk[objects[delete_id].replica[j]], objects[delete_id].size)
        objects[delete_id].isDelete = True
    sys.stdout.flush()

def do_object_write(object_unit, disk_unit, size, object_id):
    """执行对象写入操作（寻找空闲位置存储）"""
    # 实现策略：
    # 1. 顺序查找磁盘空闲位置
    # 2. 保证写入指定大小的连续空间
    # 3. 使用断言保证写入成功
    current_write_point = 0
    # i = 1
    # while True:
    #     if disk_unit[i] == 0:
    #         disk_unit[i] = object_id
    #         current_write_point += 1
    #         object_unit[current_write_point] = i
    #         if current_write_point == size:
    #             break
    #     else:
    #         i = (i + size*current_write_point) % V + 1
    # assert (current_write_point == size)
    for i in range(1, V + 1):
        if disk_unit[i] == 0:
            disk_unit[i] = object_id
            current_write_point += 1
            object_unit[current_write_point] = i
            if current_write_point == size:
                break
    assert (current_write_point == size)

def write_action():
    """处理写入指令（包含副本分配逻辑）"""
    # 副本分配策略：
    # 使用 (object_id + j) % N + 1 决定副本分布
    # 输出格式：
    # 对象ID + 副本磁盘号 + 各副本存储位置
    warning_storage = V/10
    n_write = int(input())
    for i in range(1, n_write + 1):
        write_input = input().split()
        write_id = int(write_input[0])
        size = int(write_input[1])
        tag = int(write_input[2])
        objects[write_id].lastRequestPoint = 0
        for j in range(1, REP_NUM + 1):
            load_balance_factor = 0
            while True:
                remained_size = disk[(write_id + j + load_balance_factor) % N + 1].count(0)
                if remained_size < warning_storage:
                    load_balance_factor += 1
                else:
                    break
                if load_balance_factor >= N:
                    load_balance_factor = 0
                    warning_storage = warning_storage/2

            # objects[write_id].replica[j] = ((tag +  (size-3)*(size-3)) + load_balance_factor + j) % N + 1 # add tag
            objects[write_id].replica[j] = (write_id + j) % N + 1
            objects[write_id].unit[j] = [0 for _ in range(size + 1)]
            objects[write_id].size = size
            objects[write_id].isDelete = False
            objects[write_id].haveWriteNum = 0
            do_object_write(objects[write_id].unit[j], disk[objects[write_id].replica[j]], size, write_id)
        print(f"{write_id}")
        for j in range(1, REP_NUM + 1):
            print_next(f"{objects[write_id].replica[j]}")
            for k in range(1, size + 1):
                print_next(f" {objects[write_id].unit[j][k]}")
            print()
    sys.stdout.flush()

def read_action():
    """处理读取请求（带状态机实现）"""
    # 副本分配策略：
    # 使用 (object_id + j) % N + 1 决定副本分布
    # 输出格式：
    # 对象ID + 副本磁盘号 + 各副本存储位置
    global pending_reads, disk_point, disk_pre_token
    nRead = int(input())
    for i in range(1, nRead + 1):
        read_input = input().split()
        request_id = int(read_input[0])
        object_id = int(read_input[1])
        # 更新请求链（原有逻辑仍保留，但本次调度独立于全局 current_request/current_phase）
        req_object_ids[request_id] = object_id
        req_prev_ids[request_id] = objects[object_id].lastRequestPoint
        objects[object_id].lastRequestPoint = request_id
        req_is_dones[request_id] = False
        # 初始化每个副本的阶段（从1开始）和写入计数
        pending_reads.append({
            "request_id": request_id,
            "object_id": object_id,
            "phases": { j: 1 for j in range(1, REP_NUM+1) },
            "write_counts": { j: 0 for j in range(1, REP_NUM+1) }
        })
    
    successful_ids = []
    # 每个磁盘在本时间片拥有 token = G
    for disk_id in range(1, N + 1):
        token = G
        disk_output = ""
        # 遍历 pending_reads 中所有请求，处理该磁盘上与之关联的副本
        for req in pending_reads:
            obj = objects[req["object_id"]]
            # 对每个副本，若副本在当前磁盘，则尝试处理
            for j in range(1, REP_NUM + 1):
                if obj.replica[j] != disk_id:
                    continue
                # # 当当前副本已经完成所有阶段则跳过（假设总阶段数为 size*2+1）
                # if req["phases"][j] >= obj.size * 2 + 1:
                #     continue
                # 用 while 循环不断处理该副本，直到 token 用完或该副本阶段完成
                while token > 0 and req["phases"][j] < obj.size * 2 + 1:
                    # 根据当前阶段决定处理逻辑：
                    # 奇数阶段模拟写入操作，偶数阶段模拟读取操作
                    if req["phases"][j] % 2 == 1:  
                        # 写入阶段：查找下一个数据块位置
                        block_index = (req["phases"][j] + 1) // 2  # 块号（从1开始）
                        destination = obj.unit[j][block_index]
                        # if req["request_id"] == 2:
                        #     print(disk_point[disk_id])
                        # 计算当前位置到目标位置的步长（考虑环形磁盘）
                        if destination >= disk_point[disk_id]:
                            step = destination - disk_point[disk_id]
                        else:
                            step = V - disk_point[disk_id] + destination
                        if step == 0:
                            # 如果已经在目标位置，则直接进入下一阶段
                            req["phases"][j] += 1
                            continue
                        if step <= token:
                            # token 足够走完这一步  # 输出连续的“p”
                            disk_output += "p" * step
                            disk_point[disk_id] = destination
                            req["phases"][j] += 1
                            token -= step
                        else:
                            # token 不足，走部分步长后退出
                            disk_output += "p" * token
                            disk_point[disk_id] = (disk_point[disk_id] + token) % V
                            if disk_point[disk_id] == 0:
                                disk_point[disk_id] += 1
                            token = 0
                    else:
                        # 读取阶段
                        if token < disk_pre_token[disk_id]:
                            # token不足以处理当前读取步长，输出占位符并退出
                            disk_output += "#"
                            token = 0
                        else:
                            disk_output += "r"
                            req["write_counts"][j] += 1
                            req["phases"][j] += 1
                            token -= disk_pre_token[disk_id]
                            # 更新 disk_pre_token 和指针
                            disk_pre_token[disk_id] = max(16, math.ceil(disk_pre_token[disk_id] * 0.8))
                            disk_point[disk_id] = (disk_point[disk_id] + 1) % V 
                            if disk_point[disk_id] == 0:
                                disk_point[disk_id] += 1
                            # if req["write_counts"][j] >= obj.size:
                            #     # 当前副本的写入任务完成，输出终止标记
                            #     disk_output += "#"
        # 保证每个磁盘的输出以 '#' 结尾
        if not disk_output.endswith("#"):
            disk_output += "#"
        print(disk_output)

        # 在当前磁盘处理完后，及时将已完成的请求从 pending_reads 中移除
        # （注意：这里不输出完成结果，输出部分仍保留在后面）
        to_remove = []
        for req in pending_reads:
            obj = objects[req["object_id"]]
            # 检查：只要任一副本达到完成阶段，就认为该请求已完成
            for j in range(1, REP_NUM+1):
                if req["phases"][j] >= obj.size * 2 + 1:
                    successful_ids.append(req["request_id"])
                    to_remove.append(req)
                    break
        for req in to_remove:
            pending_reads.remove(req)

    # 输出结果：如果没有请求读取完成，输出 0；否则输出成功读取请求的个数，再换行输出每个请求的 id
    if len(successful_ids) == 0:
        print("0")
    else:
        print(len(successful_ids))
        for rid in successful_ids:
            print(rid)
    sys.stdout.flush()

    # if current_request == 0 and nRead > 0:
    #     current_request = request_id
    # if current_request == 0:
    #     for i in range(1, N + 1):
    #         print("#")
    #     print("0")
    # else:
    #     objectId = req_object_ids[current_request]
    #     shark = 0
    #     for i in range(1, N + 1):
    #         if i == objects[objectId].replica[1]:
    #             token = G
    #             time = 0
    #             while token > 0:
    #                 if current_phase % 2 == 1:
    #                     block_num = int(current_phase/ 2) + 1
    #                     # try:
    #                     destination = objects[objectId].unit[1][block_num]
    #                     # except:
    #                     #     print(objects[objectId].haveWriteNum)
    #                     if destination >= disk_point[i]:
    #                         step = destination - disk_point[i]
    #                     else:
    #                         step = V - disk_point[i] + destination  
    #                     if step < token:
    #                         print("p"*step,end="")
    #                         disk_point[i] = destination
    #                         current_phase += 1
    #                         token = token - step
    #                         if step!=0:
    #                             disk_pre_token[i] = 64
    #                         continue
    #                     elif step >= token and time == 0:
    #                         print(f"j {destination}")
    #                         disk_point[i] = destination
    #                         current_phase += 1
    #                         token = 0
    #                         disk_pre_token[i] = 64
    #                         break
    #                     elif step >= token and time != 0:
    #                         print("p"*token+"#")
    #                         disk_point[i] = (disk_point[i] + token) % V
    #                         token = 0
    #                         disk_pre_token[i] = 64
    #                         continue
    #                 else:
    #                     if token < disk_pre_token[i]:
    #                         print("#")
    #                         break
    #                     print("r",end="")
    #                     time += 1
    #                     objects[objectId].haveWriteNum += 1
    #                     current_phase += 1
    #                     token = token - disk_pre_token[i]
    #                     disk_pre_token[i] = max(16,math.ceil(disk_pre_token[i]*0.8))
    #                     disk_point[i] = (disk_point[i] + 1 ) % V
    #                     if objects[objectId].haveWriteNum >= objects[objectId].size:
    #                         print("#")
    #                         break
    #                     if token == 0:
    #                         print("#")
    #                         break
    #         else:
    #             print("#")
    #     if current_phase == objects[objectId].size * 2 + 1:
    #         if objects[objectId].isDelete:
    #             print("0")
    #         else:
    #             print(f"1\n{current_request}")
    #             objects[objectId].haveWriteNum = 0
    #             req_is_dones[current_request] = True
    #         current_request = 0
    #         current_phase = 1
    #     else:
    #         print("0")
    # sys.stdout.flush()

# ---------- 辅助函数 ----------
def print_next(message):
    """连续打印辅助函数（避免自动换行）"""
    print(f"{message}", end="")

# ---------- 主程序流程 ----------
if __name__ == '__main__':
    # 初始化参数
    user_input = input().split()
    T = int(user_input[0])  # 总运行时间片
    M = int(user_input[1])  # 参数M（具体含义需结合题目）
    N = int(user_input[2])  # 磁盘数量
    V = int(user_input[3])  # 单盘容量
    G = int(user_input[4])  # 参数G（具体含义需结合题目）

    # 跳过预处理阶段
    for item in range(1, M * 3 + 1):
        input()
    print("OK")
    sys.stdout.flush()

    # 初始化磁盘指针
    for item in range(1, N + 1):
        disk_point[item] = 1  # 初始化每个磁盘的写入位置

    # 主事件循环
    for item in range(1, T + EXTRA_TIME + 1):
        timestamp_action()  # 处理时间戳
        delete_action()     # 处理删除操作
        write_action()      # 处理写入操作
        read_action()       # 处理读取操作

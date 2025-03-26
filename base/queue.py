# TODO
class ValueQueue:
    def __init__(self):
        self.queue_high = [None] * 10
        self.queue_high_front = 0
        self.queue_high_rear = 0
        self.queue_high_size = 0
        self.values_high = [(95 + i / 2) for i in range(10, 0, -1)]

        self.queue_low = [None] * 95
        self.queue_low_front = 0
        self.queue_low_rear = 0
        self.queue_low_size = 0
        self.values_low = list(range(95, 0, -1))

    def put(self, item):
        if self.queue_high_size == 10:
            high_front_item = self.queue_high[self.queue_high_front]
            self.queue_high[self.queue_high_front] = None
            self.queue_high_front = (self.queue_high_front + 1) % 10
            self.queue_high_size -= 1

            self.queue_low[self.queue_low_rear] = high_front_item
            self.queue_low_rear = (self.queue_low_rear + 1) % 95
            self.queue_low_size += 1

        self.queue_high[self.queue_high_rear] = item
        self.queue_high_rear = (self.queue_high_rear + 1) % 10
        self.queue_high_size += 1

    def get(self):
        if self.queue_low_size > 0:
            low_front_item = self.queue_low[self.queue_low_front]
            self.queue_low[self.queue_low_front] = None
            self.queue_low_front = (self.queue_low_front + 1) % 95
            self.queue_low_size -= 1
            return low_front_item
        elif self.queue_high_size > 0:
            high_front_item = self.queue_high[self.queue_high_front]
            self.queue_high[self.queue_high_front] = None
            self.queue_high_front = (self.queue_high_front + 1) % 10
            self.queue_high_size -= 1

            self.queue_low[self.queue_low_rear] = high_front_item
            self.queue_low_rear = (self.queue_low_rear + 1) % 95
            self.queue_low_size += 1

            low_front_item = self.queue_low[self.queue_low_front]
            self.queue_low[self.queue_low_front] = None
            self.queue_low_front = (self.queue_low_front + 1) % 95
            self.queue_low_size -= 1
            return low_front_item
        return None

    def index(self, i):
        """
        获取当前队尾元素的前面第i个元素。
        先从高优先级队列查找，如果不够再从低优先级队列查找。

        :param i: 表示当前队尾元素的前面第i个元素
        :return: 查找到的元素，如果没有找到则返回None
        """
        if i < self.queue_high_size:
            # 从高优先级队列查找
            index = (self.queue_high_rear - 1 - i) % 10
            return self.queue_high[index]
        else:
            # 高优先级队列元素不足，从低优先级队列继续查找
            remaining = i - self.queue_high_size
            if remaining < self.queue_low_size:
                index = (self.queue_low_rear - 1 - remaining) % 95
                return self.queue_low[index]
        return None
# NOTE: 1. size & time & score
# NOTE: 2. continuous read
# NOTE: 3. restrict the area of scanning
# NOTE: 4. time phase & tags & total count

from math import ceil
a = [64]
for i in range(7):
    a.append(max(16, ceil(a[-1] * 0.8)))
print(a, sum(a))
print((350 - sum(a)) // 16 + 8)
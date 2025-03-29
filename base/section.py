from .config import *
from .object import *
from typing import List

class SortList(list):
    def append_ascending(self, item: int):
        left, right = 0, len(self) - 1
        while left <= right:
            mid = (left + right) // 2
            if self[mid] == item:
                left = right = mid
                break
            elif self[mid] < item:
                left = mid + 1
            else:
                right = mid - 1
        self.insert(left, item)

# TODO
class Section:   # disk section for picking valuable blocks
    def __init__(self, idx: int, start_pos: int, size: int, units: List[Unit]):
        self.id: int = idx
        self.start_pos: int = start_pos
        self.max_written_pos: int = start_pos - 1
        self.section_size: int = size
        self.end_pos: int = start_pos + size - 1

        self.data: List[Unit] = units
        self.max_obj_size: int = MAX_OBJECT_SIZE
        self.delete_record: Dict[int, SortList] = {s: SortList() for s in range(1, self.max_obj_size + 1)}

    def get_unit(self, i: int) -> Unit:
        assert self.start_pos <= i <= self.end_pos, f'{self.start_pos} <= {i} <= {self.end_pos}'
        return self.data[i - self.start_pos]

    def recycle_unit(self, unit_id: int, size: int):
        if size > self.max_obj_size:
            for s in range(self.max_obj_size + 1, size + 1):
                self.delete_record[s] = []
            self.max_obj_size = size
        assert type(unit_id) == int, f'{unit_id}: {type(unit_id)}'
        self.delete_record[size].append_ascending(unit_id)

    def register_max_written_pos(self, units: List[Unit]):
        for unit in units:
            self.max_written_pos = max(self.max_written_pos, unit.id)

    def reuse_n_units(self, n: int, separate: bool = False) -> List[Unit]:
        if not separate:
            for size in range(n, self.max_obj_size + 1):  #
                if len(self.delete_record[size]) > 0:
                    start_pos: int = self.delete_record[size].pop(0)
                    assert type(start_pos) == int and type(n) == int, f'{start_pos}: {type(start_pos)}, {n}: {type(n)}, {size} -> {self.delete_record[size]}'
                    units: List[Unit] = [self.get_unit(i) for i in range(start_pos, start_pos + n)]
                    if size != n:
                        self.delete_record[size - n].append_ascending(start_pos + n)
                    return units
            return None
        else:
            unit_size: List[int] = []
            n_size: int = n
            sizes: Dict[int, int] = {s: len(self.delete_record[s]) for s in self.delete_record.keys() if (s < n) and len(self.delete_record[s]) > 0}
            while (n > 0):
                if len(sizes.keys()) == 0 or min(sizes.keys()) > n:
                    return None
                max_size: int = max([k for k in sizes.keys() if k <= n])
                sizes[max_size] -= 1
                if sizes[max_size] == 0:
                    sizes.pop(max_size)
                unit_size.append(max_size)
                n -= max_size
            units: List[Unit] = []
            for size in unit_size:
                units.extend(self.reuse_n_units(size, separate=False))
            assert len(units) == n_size, f'{len(units)} vs {n_size}, unit_size={unit_size}, sizes={sizes}'
            return units

    def find_n_empty_units(self, n: int) -> List[Unit]:
        units: List[Unit] = self.reuse_n_units(n, separate=False)
        if units is not None:
            return units
        if self.max_written_pos + n <= self.end_pos:
            start_pos: int = self.max_written_pos + 1
            units = [self.get_unit(i) for i in range(start_pos, start_pos + n)]
            return units
        return self.reuse_n_units(n, separate=True)
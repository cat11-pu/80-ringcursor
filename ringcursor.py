"""ringcursor.py：定容环形缓冲。

记录按单调递增的全局序号写入固定长度槽位；写满容量后覆盖最旧记录并累计
``overwritten``。游标记录“下一条要读的序号”，读取时惰性检测是否已被覆盖。
内存只与 ``capacity`` 相关，不随累计写入量增长。
"""
from __future__ import annotations

import json


class Ring:
    def __init__(self, capacity: int = 5):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._slots = [None] * capacity
        self._head = 0        # 下一条写入将使用的全局序号
        self._oldest = 0      # 当前最旧可用记录的序号
        self.overwritten = 0
        self.cursors = {}

    def append(self, payload: str) -> dict:
        """写入一条记录；缓冲满时覆盖最旧记录。"""
        if self._head - self._oldest >= self.capacity:
            self._oldest += 1
            self.overwritten += 1
        self._slots[self._head % self.capacity] = payload
        self._head += 1
        return {"size": self._head - self._oldest}

    def open_cursor(self, name: str) -> dict:
        """在当前最旧可用位置打开（或重置）游标。"""
        self.cursors[name] = self._oldest
        return {"position": self._oldest}

    def read(self, name: str, count: int) -> dict:
        """从游标位置顺序读取至多 ``count`` 条并前移游标。

        游标位置若已被覆盖（早于最旧可用位置），返回 ``valid: False`` 与空
        记录，并把游标重置到最旧可用位置；绝不返回覆盖槽位上的新数据。
        """
        position = self.cursors[name]
        if position < self._oldest:
            self.cursors[name] = self._oldest
            return {"valid": False, "records": []}
        available = self._head - position
        n = min(count, available)
        if n < 0:
            n = 0
        records = [
            self._slots[seq % self.capacity]
            for seq in range(position, position + n)
        ]
        self.cursors[name] = position + n
        return {"valid": True, "records": records}

    def persist(self) -> bytes:
        """把缓冲内容、覆盖计数与全部游标位置序列化为字节快照。"""
        snapshot = {
            "capacity": self.capacity,
            "head": self._head,
            "oldest": self._oldest,
            "overwritten": self.overwritten,
            "slots": self._slots,
            "cursors": self.cursors,
        }
        return json.dumps(snapshot, ensure_ascii=False).encode("utf-8")

    def restore(self, blob: bytes = None) -> dict:
        """从 ``persist()`` 的字节快照恢复，并返回统计信息。"""
        data = json.loads(blob.decode("utf-8"))
        self.capacity = data["capacity"]
        slots = list(data["slots"])
        if len(slots) < self.capacity:
            slots.extend([None] * (self.capacity - len(slots)))
        self._slots = slots[: self.capacity]
        self._head = data["head"]
        self._oldest = data["oldest"]
        self.overwritten = data["overwritten"]
        self.cursors = dict(data["cursors"])
        return self.stats()

    def stats(self) -> dict:
        return {
            "capacity": self.capacity,
            "size": self._head - self._oldest,
            "overwritten": self.overwritten,
            "cursors": len(self.cursors),
        }

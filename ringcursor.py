"""ringcursor.py：环形缓冲内核（容量固定，写满覆盖最旧记录）。"""
from __future__ import annotations

import json


class Ring:
    def __init__(self, capacity: int = 5):
        if capacity < 1:
            raise ValueError("capacity 必须 >= 1")
        self.capacity = capacity
        self.overwritten = 0
        self.cursors = {}
        self._buf = []
        self._head = 0
        self._total = 0

    def _oldest(self) -> int:
        """最旧可用记录的绝对序号。"""
        return self._total - len(self._buf)

    def append(self, payload: str) -> dict:
        """写入一条记录；写满后覆盖最旧记录并计入 overwritten。"""
        if len(self._buf) < self.capacity:
            self._buf.append(payload)
        else:
            self._buf[self._head] = payload
            self._head = (self._head + 1) % self.capacity
            self.overwritten += 1
        self._total += 1
        return {"size": len(self._buf)}

    def open_cursor(self, name: str) -> dict:
        """在当前最旧可用位置打开（或重置）游标。"""
        position = self._oldest()
        self.cursors[name] = position
        return {"name": name, "position": position}

    def read(self, name: str, count: int) -> dict:
        """从游标位置读最多 count 条；游标已被覆盖则本次读失效。"""
        if name not in self.cursors:
            raise KeyError(f"未知游标: {name!r}")
        position = self.cursors[name]
        oldest = self._oldest()
        if position < oldest:
            self.cursors[name] = oldest
            return {"records": [], "valid": False}
        available = self._total - position
        n = max(0, min(count, available))
        start = (self._head + (position - oldest)) % self.capacity
        records = [self._buf[(start + i) % self.capacity] for i in range(n)]
        self.cursors[name] = position + n
        return {"records": records, "valid": True}

    def persist(self) -> bytes:
        """落盘快照：缓冲内容、覆盖计数与游标位置。"""
        snapshot = {
            "capacity": self.capacity,
            "overwritten": self.overwritten,
            "cursors": dict(self.cursors),
            "buf": list(self._buf),
            "head": self._head,
            "total": self._total,
        }
        return json.dumps(snapshot, ensure_ascii=False).encode("utf-8")

    def restore(self, blob: bytes = None) -> dict:
        """从快照恢复；blob 为 None 时保持现状。"""
        if blob is not None:
            snapshot = json.loads(blob.decode("utf-8"))
            self.capacity = snapshot["capacity"]
            self.overwritten = snapshot["overwritten"]
            self.cursors = dict(snapshot["cursors"])
            self._buf = list(snapshot["buf"])
            self._head = snapshot["head"]
            self._total = snapshot["total"]
        return self.stats()

    def stats(self) -> dict:
        return {"capacity": self.capacity, "size": len(self._buf),
                "overwritten": self.overwritten, "cursors": len(self.cursors)}

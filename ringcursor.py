"""ringcursor.py：环形缓冲（基线：无限追加）。"""
from __future__ import annotations


class Ring:
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.records = []
        self.overwritten = 0
        self.cursors = {}

    def append(self, payload: str) -> dict:
        """基线：一直追加，永不覆盖。"""
        self.records.append(payload)
        return {"size": len(self.records)}

    def open_cursor(self, name: str) -> dict:
        raise NotImplementedError("游标还没实现")

    def read(self, name: str, count: int) -> dict:
        raise NotImplementedError("按游标读还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"capacity": self.capacity, "size": len(self.records),
                "overwritten": self.overwritten, "cursors": len(self.cursors)}

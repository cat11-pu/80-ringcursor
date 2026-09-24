"""ringapi.py：对外门面（老接口 append 不能改）。"""
from __future__ import annotations

from ringcursor import Ring


class Log:
    def __init__(self, capacity: int = 5):
        self.ring = Ring(capacity)

    def append(self, payload: str) -> dict:
        return self.ring.append(payload)

    def open_cursor(self, name: str) -> dict:
        return self.ring.open_cursor(name)

    def read(self, name: str, count: int) -> dict:
        return self.ring.read(name, count)

    def snapshot(self) -> bytes:
        return self.ring.persist()

    def rebuild(self, blob: bytes = None) -> dict:
        return self.ring.restore(blob)

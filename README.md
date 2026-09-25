# ringcursor

纯 Python 标准库的 ringcursor。

## 用法

    from ringcursor import Ring

    ring = Ring(capacity=4)        # 容量固定，写满后覆盖最旧记录
    ring.append("r1")              # -> {"size": 1}
    ring.open_cursor("c1")         # 在当前最旧可用位置打开游标
    ring.read("c1", 2)             # -> {"records": [...], "valid": True}
    # 游标位置已被覆盖时：{"records": [], "valid": False}，游标重置到最旧可用位置
    blob = ring.persist()          # 落盘快照（bytes）
    ring.restore(blob)             # 重启恢复：内容、覆盖计数、游标位置一致
    ring.stats()                   # {"capacity", "size", "overwritten", "cursors"}

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py

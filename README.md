# ringcursor

纯 Python 标准库的 ringcursor：定容环形缓冲 + 按位置顺序读取的游标。

## 用法

```python
from ringcursor import Ring

ring = Ring(capacity=4)
ring.append("r1")                 # 写满后覆盖最旧记录，覆盖数计入 overwritten
ring.open_cursor("c1")            # 在当前最旧可用位置打开游标
ring.read("c1", 2)                # -> {"valid": True, "records": [...]}，游标前移
blob = ring.persist()             # 落盘快照（bytes）
reborn = Ring(4).restore(blob)    # 恢复内容、overwritten 与游标位置
ring.stats()                      # capacity / size / overwritten / cursors
```

- 内存恒为 `capacity` 条，与累计写入总量无关；读取为 O(读取条数)。
- 游标若已落在被覆盖的位置，`read` 返回 `{"valid": False, "records": []}`
  并把游标重置到最旧可用位置。
- 请求条数超过可用时按实际可用条数返回，不等待、不报错。

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py

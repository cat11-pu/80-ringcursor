"""check_sample.py：按 sample/ops.json 走一圈，打印验收面。"""
import json
import os
import sys

from ringcursor import Ring


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "ops.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    ring = Ring(spec["capacity"])
    reads = []
    for step in spec["ops"]:
        if step["op"] == "append":
            ring.append(step["payload"])
        elif step["op"] == "open":
            ring.open_cursor(step["name"])
        else:
            reads.append((step["name"], ring.read(step["name"], step["count"])))
    blob = ring.persist()
    reborn = Ring(spec["capacity"])
    restored = reborn.restore(blob)
    print("按游标读取 =", [(name, result.get("records"), result.get("valid")) for name, result in reads])
    print("失效的游标 =", [name for name, result in reads if result.get("valid") is False])
    print("被覆盖的条数 =", ring.stats().get("overwritten"))
    print("缓冲内剩余条数 =", ring.stats().get("size"))
    print("缓冲容量 =", spec["capacity"])
    print("恢复后的条数 =", restored.get("size"))
    print("恢复后的覆盖计数 =", restored.get("overwritten"))
    print("不变量（读到的都是未覆盖记录） =", spec["cursor_invariant"])
    print("读完的记录数 =", sum(len(result.get("records") or []) for _, result in reads))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

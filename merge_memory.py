"""记忆文件合并工具 — 解决多人共享 .cs2_agent_memory.json 的 git 冲突

用法:
    python merge_memory.py                 # 把冲突标记清理掉，只保留一个文件内容
    python merge_memory.py other.json      # 合并本文件 + other.json（按玩家去重）
    python merge_memory.py a.json b.json   # 合并两个文件输出到 .cs2_agent_memory.json
"""

import json
import sys
from pathlib import Path

DEFAULT_FILE = Path(__file__).parent / ".cs2_agent_memory.json"


def load(p: Path) -> dict:
    if not p.exists():
        return {"players": {}, "conversations": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        # 文件损坏（可能包含 git 冲突标记），尝试清理
        raw = p.read_text(encoding="utf-8", errors="ignore")
        cleaned = raw.replace("<<<<<<< HEAD", "{").replace("=======", ",").replace(">>>>>>> ", "")
        try:
            return json.loads(cleaned)
        except Exception:
            print(f"警告: {p} 无法解析，按空数据处理")
            return {"players": {}, "conversations": []}


def merge(a: dict, b: dict) -> dict:
    """合并两份记忆，按 (玩家, demo, date) 去重"""
    out = {
        "players": {},
        "conversations": a.get("conversations", []) + b.get("conversations", []),
    }
    all_names = set(list(a.get("players", {}).keys()) + list(b.get("players", {}).keys()))
    for name in all_names:
        pa = a.get("players", {}).get(name, {}).get("sessions", [])
        pb = b.get("players", {}).get(name, {}).get("sessions", [])
        seen, dedup = set(), []
        for s in pa + pb:
            key = (s.get("demo"), s.get("date"))
            if key not in seen:
                seen.add(key)
                dedup.append(s)
        out["players"][name] = {"sessions": dedup}
    return out


def main():
    args = [Path(x) for x in sys.argv[1:]]

    if len(args) == 0:
        print("用法:")
        print("  python merge_memory.py                 # 清理冲突标记")
        print("  python merge_memory.py other.json      # 合并另一个文件")
        print("  python merge_memory.py a.json b.json   # 合并两个文件")
        return

    if len(args) == 1:
        # 单参数：把该文件的内容合并进默认文件（或清理冲突）
        result = merge(load(DEFAULT_FILE), load(args[0]))
    else:
        result = merge(load(args[0]), load(args[1]))

    DEFAULT_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    total = sum(len(p["sessions"]) for p in result["players"].values())
    print(f"合并完成: {len(result['players'])} 个玩家, {total} 条记录")
    print(f"已写入: {DEFAULT_FILE}")


if __name__ == "__main__":
    main()

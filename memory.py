""" 记忆系统 — 长期记忆（文件）+ 短期记忆（上下文管理） """

import json
import time
from pathlib import Path

MEMORY_FILE = Path.home() / ".cs2_agent_memory.json"


def load_memory():
    """加载长期记忆."""
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"players": {}, "conversations": []}


def save_memory(memory):
    """保存长期记忆."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_session(memory, player_name, coach_data, llm_response="", demo_name=""):
    """将本次分析存入长期记忆（含去重：同个玩家+同文件名不重复记录）."""
    if player_name not in memory["players"]:
        memory["players"][player_name] = {"sessions": []}

    # ── 去重检查：最近一条跟本次是同文件则跳过 ──
    sessions = memory["players"][player_name]["sessions"]
    if demo_name and sessions:
        last = sessions[-1]
        if last.get("demo") == demo_name:
            return  # 同文件不重复记录

    session = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "demo": demo_name,
        "kills": coach_data["kills"],
        "deaths": coach_data["deaths"],
        "kd": coach_data["kd"],
        "hs_pct": coach_data["hs_pct"],
        "top_weapon": coach_data["top_weapon"],
        "utility_kills": coach_data["utility_kills"],
        "llm_snippet": (llm_response or "")[:200],
    }
    sessions.append(session)
    if len(sessions) > 50:
        memory["players"][player_name]["sessions"] = sessions[-50:]
    save_memory(memory)


def get_history(memory, player_name):
    """获取某玩家的历史记录."""
    p = memory["players"].get(player_name)
    return p["sessions"] if p and p["sessions"] else None


def format_history(sessions, limit=5):
    """历史记录格式化为文本."""
    if not sessions:
        return "暂无历史数据"
    lines = ["## 历史比赛记录"]
    for s in sessions[-limit:]:
        lines.append(
            f"- [{s['date']}] {s['kills']}K/{s['deaths']}D "
            f"K/D {s['kd']} HS% {s['hs_pct']}% 主武器: {s['top_weapon']}"
        )
    return "\n".join(lines)


def manage_short_term(messages, max_turns=20):
    """管理短期记忆：保留 system + 最近 N 轮对话."""
    if len(messages) > 2 + max_turns * 2:
        keep = [messages[0]] + messages[-(max_turns * 2):]
        return keep
    return messages

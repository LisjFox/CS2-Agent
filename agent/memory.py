"""多轮对话记忆管理"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationMemory:
    """基于滑动窗口的对话记忆管理"""

    def __init__(self, max_window: int = 10):
        self.max_window = max_window
        self.history: List[Dict] = []
        self.context: Dict = {
            "current_map": None,    # 当前讨论的地图
            "current_side": None,   # 当前讨论的阵营
            "last_topic": None,     # 上次讨论的主题
            "mentioned_weapons": [],  # 提到过的武器
        }

    def add_turn(self, role: str, content: str):
        """添加一轮对话"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # 滑动窗口：保留最近 N 轮
        if len(self.history) > self.max_window * 2:
            self.history = self.history[-(self.max_window * 2):]

    def update_context(self, user_input: str, assistant_response: str = ""):
        """从对话中提取上下文信息"""
        text = (user_input + " " + assistant_response).lower()

        # 识别地图
        maps = ["mirage", "dust2", "inferno", "nuke", "ancient", "anubis", "overpass", "vertigo"]
        for m in maps:
            if m in text:
                self.context["current_map"] = m.capitalize()
                break

        # 识别阵营
        if "t 侧" in text or "t方" in text or "匪" in text or "进攻方" in text:
            self.context["current_side"] = "T"
        elif "ct 侧" in text or "ct方" in text or "警" in text or "防守方" in text:
            self.context["current_side"] = "CT"

        # 识别武器
        weapons = ["ak-47", "ak47", "m4a4", "m4a1-s", "awp", "deagle", "沙漠之鹰",
                    "famas", "galil", "sg 553", "aug", "mac-10", "mp9", "p90",
                    "usp-s", "glock", "p250", "fiveseven", "tec-9"]
        for w in weapons:
            if w in text and w not in [x.lower() for x in self.context["mentioned_weapons"]]:
                self.context["mentioned_weapons"].append(w)

    def get_history(self) -> List[Dict]:
        """获取完整对话历史"""
        return self.history

    def get_recent_context(self, n: int = 3) -> List[Dict]:
        """获取最近 N 轮对话"""
        recent = self.history[-(n * 2):] if len(self.history) > n * 2 else self.history
        return recent

    def get_context_summary(self) -> str:
        """生成上下文摘要，用于 LLM 提示"""
        parts = []
        if self.context["current_map"]:
            parts.append(f"当前地图：{self.context['current_map']}")
        if self.context["current_side"]:
            parts.append(f"当前阵营：{self.context['current_side']}")
        if self.context["mentioned_weapons"]:
            parts.append(f"提到过的武器：{', '.join(self.context['mentioned_weapons'][-3:])}")
        if self.context["last_topic"]:
            parts.append(f"上一轮主题：{self.context['last_topic']}")

        return "，".join(parts) if parts else ""

    def clear(self):
        """清空记忆"""
        self.history.clear()
        self.context = {
            "current_map": None,
            "current_side": None,
            "last_topic": None,
            "mentioned_weapons": [],
        }


# 全局单例
_memory: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """获取全局对话记忆实例"""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
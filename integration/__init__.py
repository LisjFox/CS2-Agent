"""
尚鸣惊人 — 知识库 + 数据分析 集成层
=====================================

本文件定义了"潘一鸣"（知识库/战术分析）和"李尚基"（Demo解析/数据提取）
两部分之间的标准接口。

工作流程:
  1. Demo解析 → 找残局回合 → 提取回合上下文
  2. 上下文 → 传给战术分析模块 → 得到战术指导
  3. 战术指导 + 数据报告 → 输出给用户
"""

# ═══════════════════════════════════════════════════
#  回合上下文 — 你那边提供给潘一鸣的数据格式
# ═══════════════════════════════════════════════════

"""
一个典型回合上下文的例子：

{
    "round": 8,
    "map": "de_dust2",
    "phase": "clutch_1v2",
    "tick": 45231,
    "time_display": "1:15",
    
    "you": {
        "name": "基666",
        "health": 45,
        "armor": 50,
        "has_helmet": true,
        "weapon": "ak-47",
        "ammo_clip": 15,
        "ammo_reserve": 30,
        "equip_value": 4200,
        "position": {"x": 1250, "y": 850},
        "kills_this_round": 2
    },
    
    "alive_players": [
        {"name": "DONKING", "team": "CT", "health": 75, "weapon": "m4a4", "position": {"x": 1400, "y": 900}},
        {"name": "encore", "team": "CT", "health": 100, "weapon": "awp", "position": {"x": 1100, "y": 750}},
    ],
    
    "dead_players": ["我是上等马", "我头上有磁铁？"],
    
    "score": {"T": 4, "CT": 3},
    "bomb_status": "planted",      # "carried" / "planted" / "exploded" / "defused"
    "bomb_site": "A",
    "round_winner": None,           # 未知（还没打完）
    
    "known_info": "我下完A包，躲在箱子后。CT中门出了一个，拱门可能还有一个",
    "recommended_role": "残局防守者",
}
"""


# ═══════════════════════════════════════════════════
#  战术指导 — 潘一鸣那边返回给我们的数据格式
# ═══════════════════════════════════════════════════

"""
一个典型战术指导的例子：

{
    "assessment": "劣势残局，2v1，你在A包点，CT从两个方向夹击",
    "difficulty": "hard",
    
    "recommended_action": "利用烟雾弹封住拱门，只架一个方向",
    "position_to_hold": "A包点箱子后，面向中路",
    
    "utility_to_use": [
        {"item": "烟雾弹", "target": "拱门", "description": "封住拱门视线"},
        {"item": "燃烧弹", "target": "A大", "description": "阻止A大CT推进"},
    ],
    
    "likely_enemy_positions": [
        "CT可能从拱门出",
        "CT可能在A大架枪",
    ],
    
    "reference": "参考 NiKo 在 IEM Katowice 2024 的残局处理",
    
    "alternative": "也可以退到B包点保枪，但2v1建议打",
    "common_mistake": "不要换位太频繁，容易被人抓timing",
}
"""


# ═══════════════════════════════════════════════════
#  TacticalCoach — 潘一鸣需要实现的接口
# ═══════════════════════════════════════════════════

class TacticalCoach:
    """
    战术教练接口。
    ===============
    潘一鸣，你需要实现这个类的以下方法。
    写好之后，把 `knowledge_base/` 和 `tactical_reasoner.py` 放到这个目录下，
    然后修改 imports 导入你自己的实现。
    
    你的输入是：
      - round_context（回合上下文，包含你当时能看到的所有信息）
      - 你的知识库（地图/道具/武器/战术）
    
    你的输出是：
      - tactical_advice（战术指导）
    """

    def __init__(self):
        """初始化你的知识库和推理引擎."""
        pass

    def analyze(self, round_context: dict) -> dict:
        """
        分析一个回合，给出战术指导。

        参数:
            round_context: 你那边提供的回合上下文 dict
                (格式见上面的 Round Context 定义)

        返回:
            tactical_advice: 战术指导 dict
                (格式见上面的 Tactical Advice 定义)
        """
        # ── 你在这里写你的逻辑 ──
        # 1. 从 round_context 提取关键信息
        # 2. 查询你的知识库
        # 3. 用 LLM 或规则引擎推理
        # 4. 返回战术指导

        raise NotImplementedError("潘一鸣，请实现 analyze 方法")

    def find_clutch_rounds(self, demo_analysis: dict) -> list[int]:
        """
        从整场数据中找出值得分析的残局回合。

        参数:
            demo_analysis: 你那边的 demo 全量分析数据
                (包含每回合的击杀时间线、玩家存亡变化等)

        返回:
            list[int]: 值得分析的回合号列表
        """
        raise NotImplementedError("潘一鸣，请实现 find_clutch_rounds 方法")


# ═══════════════════════════════════════════════════
#  集成入口 — 两边合体后的调用方式
# ═══════════════════════════════════════════════════

class IntegratedCoach:
    """合体教练 — 李尚基解析数据 + 潘一鸣战术分析."""

    def __init__(self, tactical_coach: TacticalCoach = None):
        self.tactical_coach = tactical_coach

    def analyze_demo(self, demo_path: str, player_filter: str = None):
        """完整分析流程."""
        # 1. 你的部分：解析 Demo
        from parser import parse_demo
        from analysis import build_coach_data
        from snapshot import DemoSnapshot
        from memory import load_memory, get_history, format_history

        data = parse_demo(demo_path)

        # 2. 找目标玩家
        player_sid = None
        if player_filter:
            for sid, p in data["player_stats"].items():
                if player_filter in p["name"]:
                    player_sid = sid
                    break
        if not player_sid:
            player_sid = max(data["player_stats"].keys(),
                             key=lambda sid: data["player_stats"][sid]["kills"])
        player_name = data["player_stats"][player_sid]["name"]

        # 3. 执行战术分析（如果潘一鸣的部分已接入）
        tactical_results = []
        if self.tactical_coach:
            snapshot = DemoSnapshot(demo_path)
            clutch_rounds = self.tactical_coach.find_clutch_rounds(data)

            for rnd in clutch_rounds:
                # 提取第 rnd 回合的关键时刻（比如最后交火时刻）
                # 这里暂时用回合中点作为示意
                state = snapshot.get_tick_state(rnd, 45)
                round_context = self._build_context(state, player_name)
                advice = self.tactical_coach.analyze(round_context)
                tactical_results.append({
                    "round": rnd,
                    "context": round_context,
                    "advice": advice,
                })

        return {
            "player_name": player_name,
            "player_data": build_coach_data(data, player_sid),
            "tactical_analysis": tactical_results,
        }

    def _build_context(self, snapshot_state, player_name):
        """把时刻快照转成回合上下文."""
        if "error" in snapshot_state:
            return None

        # 找你自己
        you = None
        for p in snapshot_state.get("all_players", []):
            if p["name"] == player_name:
                you = p
                break

        alive = [p for p in snapshot_state.get("all_players", [])
                 if p["health"] > 0]

        return {
            "round": snapshot_state.get("round", 0),
            "map": snapshot_state.get("map", ""),
            "phase": f"{len([p for p in alive if p['team'] == 3])}v{len([p for p in alive if p['team'] == 2])}",
            "time_display": snapshot_state.get("time_display", ""),
            "you": you,
            "alive_players": alive,
            "dead_players": [p["name"] for p in snapshot_state.get("all_players", [])
                            if p["health"] == 0],
            "bomb_status": "unknown",
            "known_info": "（潘一鸣的逻辑会补充更多已知信息）",
        }

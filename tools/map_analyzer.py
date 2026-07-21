"""地图分析工具：地图点位解析、攻防策略分析"""

from typing import Dict, List, Optional
from knowledge_base.data.maps import MAP_KNOWLEDGE, AVAILABLE_MAPS
from langchain_core.tools import tool


# 地图别名映射
MAP_ALIASES = {
    # 中文标准名
    "荒漠迷城": "Mirage", "炙热沙城": "Dust2", "炼狱小镇": "Inferno",
    "核子危机": "Nuke", "远古遗迹": "Ancient", "阿努比斯": "Anubis",
    "死亡游乐园": "Overpass", "眩晕大厦": "Vertigo",
    # 中文俗称
    "米垃圾": "Mirage", "迷城": "Mirage",
    "沙二": "Dust2", "沙漠": "Dust2", "沙城": "Dust2", "dust": "Dust2",
    "小镇": "Inferno", "inferno": "Inferno",
    "核子": "Nuke", "核弹": "Nuke",
    "遗迹": "Ancient",
    "游乐园": "Overpass", "乐园": "Overpass",
    "大厦": "Vertigo",
    # 英文简写
    "dust": "Dust2", "mirage": "Mirage",
}


def _normalize_map_name(name: str) -> str:
    """统一地图名称，支持别名"""
    if not name:
        return ""
    # 检查别名
    if name in MAP_ALIASES:
        return MAP_ALIASES[name]
    # 标准名称标准化
    return name


@tool
def analyze_map(map_name: str, topic: str = "overview") -> Dict:
    """分析指定地图的信息

    Args:
        map_name: 地图名称（如 "Mirage", "Dust2"）
        topic: 分析主题（overview/callouts/tactics/ct_default/all）

    Returns:
        地图分析结果
    """
    if not map_name:
        return {
            "found": False,
            "message": f"未指定地图。可用地图：{', '.join(AVAILABLE_MAPS)}",
            "available_maps": AVAILABLE_MAPS,
        }
    map_name = _normalize_map_name(map_name)
    map_name_normalized = map_name.lower().replace(" ", "").replace("-", "")
    matched = []
    for item in MAP_KNOWLEDGE:
        item_map = item.get("map", "").lower().replace(" ", "").replace("-", "")
        if item_map == map_name_normalized:
            matched.append(item)

    if not matched:
        return {
            "found": False,
            "message": f"未找到地图「{map_name}」的信息。可用地图：{', '.join(AVAILABLE_MAPS)}",
            "available_maps": AVAILABLE_MAPS,
        }

    if topic == "all":
        results = matched
    else:
        topic_map = {
            "overview": "地图概述",
            "callouts": "报点",
            "tactics": "战术",
            "ct_default": "CT",
        }
        keyword = topic_map.get(topic, topic)
        results = [m for m in matched if keyword in m.get("category", "") or keyword in m.get("title", "")]
        if not results:
            results = matched  # 找不到匹配主题就返回全部

    return {
        "found": True,
        "map": map_name,
        "results": [
            {
                "title": r["title"],
                "category": r["category"],
                "content": r["content"],
            }
            for r in results
        ],
    }


@tool
def get_tactical_advice(
    map_name: str,
    side: str,
    situation: str,
    equipment: Optional[List[str]] = None,
) -> str:
    """根据场景给出战术建议

    Args:
        map_name: 地图名称
        side: "T" 或 "CT"
        situation: 场景描述（如 "进攻A点", "防守B点", "eco局", "残局1v2"）
        equipment: 拥有的装备列表（可选）

    Returns:
        战术建议文本
    """
    if not map_name:
        map_name = "Mirage"
    else:
        map_name = _normalize_map_name(map_name)
    map_info = analyze_map(map_name, "all")
    if not map_info["found"]:
        return map_info["message"]

    # 根据场景给出通用建议
    advice_parts = [f"【{map_name}】{side}侧 {situation} 战术建议：\n"]

    if "eco" in situation.lower():
        if side == "T":
            advice_parts.append(
                "💰 经济局建议：\n"
                "- 全队走一起，用人数优势换枪\n"
                "- 可以 rush 一个点，打 CT 措手不及\n"
                "- MAC-10/P250/Tec-9 都是好的选择\n"
                "- 目标是下包 + 杀人换枪，即使输了下一局经济也会更好"
            )
        else:
            advice_parts.append(
                "💰 经济局建议：\n"
                "- 可以前压或近点阴人\n"
                "- MP9/MAG-7/Five-SeveN 是好的选择\n"
                "- 利用掩体和 CT 熟悉地形的优势\n"
                "- 目标是换掉对手的枪，打乱 T 的经济节奏"
            )

    if "残局" in situation or "1v" in situation:
        advice_parts.append(
            "🎯 残局建议：\n"
            "- 保持冷静，利用时间差\n"
            "- 利用声音信息判断敌人位置\n"
            "- 不要轻易暴露自己的位置\n"
            "- 时间充裕时可以假拆/假下包骗对手出来\n"
            "- 收集信息后再做决定"
        )

    if "防守" in situation:
        if map_name == "Mirage":
            advice_parts.append(
                "🛡️ Mirage 防守要点：\n"
                "- 中路是最关键的位置，控制中路信息\n"
                "- A 点防守注意 A Ramp 和 A 二楼两个方向\n"
                "- B 点防守可以先丢雷/火拖延，等队友回防\n"
                "- 连接 Connector 可以快速转点协防"
            )
        elif map_name == "Dust2":
            advice_parts.append(
                "🛡️ Dust2 防守要点：\n"
                "- A Long 控制权是关键，CT 可以 peek 拿信息\n"
                "- B 点防守先丢拖延道具\n"
                "- 中路 CT 可以协防 A 和 B\n"
                "- B Tunnel 和 A Long 是 T 的主要进攻路线"
            )
        elif map_name == "Inferno":
            advice_parts.append(
                "🛡️ Inferno 防守要点：\n"
                "- Banana 控制权是关键\n"
                "- A 点防守注意 A 二楼和教堂两个方向\n"
                "- CT 可以通过中路快速转点\n"
                "- 燃烧弹在 Inferno 极为重要"
            )

    if "进攻" in situation:
        if map_name == "Mirage":
            advice_parts.append(
                "⚔️ Mirage 进攻要点：\n"
                "- A 点进攻需要 CT 烟 + Jungle 烟\n"
                "- B 点进攻需要控制 Banana\n"
                "- 中路控制是夹击 A 和 B 的关键\n"
                "- 假打和转点是非常有效的战术"
            )
        elif map_name == "Dust2":
            advice_parts.append(
                "⚔️ Dust2 进攻要点：\n"
                "- A Long 控制权是打 A 的关键\n"
                "- B Tunnel 控制权是打 B 的关键\n"
                "- 中路控制可以打 A Short 或夹 B\n"
                "- 快速转点打 CT 回防的时间差"
            )
        elif map_name == "Inferno":
            advice_parts.append(
                "⚔️ Inferno 进攻要点：\n"
                "- Banana 控制是 B 点进攻的前提\n"
                "- A 二楼进攻需要 CT 烟 + Arch 烟\n"
                "- 中路控制可以配合 Banana 或 A 二楼\n"
                "- 燃烧弹清点和封锁非常有效"
            )

    return "\n\n".join(advice_parts)


# 工具注册信息
TOOL_META = {
    "name": "map_analyzer",
    "description": "CS2 地图分析和战术建议工具。可以查询地图点位、报点、进攻和防守策略。",
    "parameters": {
        "map_name": "地图名称",
        "topic": "分析主题（overview/callouts/tactics/ct_default/all）",
        "side": "阵营（T/CT），用于战术建议",
        "situation": "场景描述",
    },
}
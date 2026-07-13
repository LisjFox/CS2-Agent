"""枪械对比工具：比较武器参数，推荐最佳选择"""

from typing import Dict, List, Optional
from knowledge_base.data.weapons import WEAPON_CATEGORIES


# 武器核心参数数据库
WEAPON_STATS = {
    "AK-47": {
        "price": 2700, "side": "T", "type": "步枪",
        "damage": {"head": 140, "chest": 36, "stomach": 45, "leg": 28},
        "armor_pen": 77.5, "mag_size": 30, "fire_rate": 600,
        "reload_time": 2.5, "kill_reward": 300,
        "pros": "一枪爆头必杀，威力大", "cons": "后坐力大，远距离需压枪",
    },
    "M4A4": {
        "price": 3100, "side": "CT", "type": "步枪",
        "damage": {"head": 140, "chest": 33, "stomach": 41, "leg": 25},
        "armor_pen": 70, "mag_size": 30, "fire_rate": 666,
        "reload_time": 3.1, "kill_reward": 300,
        "pros": "射速快，弹道密集", "cons": "远距离爆头不致死，换弹慢",
    },
    "M4A1-S": {
        "price": 3100, "side": "CT", "type": "步枪",
        "damage": {"head": 140, "chest": 38, "stomach": 47, "leg": 28},
        "armor_pen": 70, "mag_size": 25, "fire_rate": 600,
        "reload_time": 3.1, "kill_reward": 300,
        "pros": "消音器无声，后坐力小，精度高", "cons": "弹匣仅25发，备弹75发",
    },
    "AWP": {
        "price": 4750, "side": "both", "type": "狙击步枪",
        "damage": {"head": 459, "chest": 115, "stomach": 143, "leg": 86},
        "armor_pen": 97.5, "mag_size": 10, "fire_rate": 41,
        "reload_time": 3.7, "kill_reward": 100,
        "pros": "上半身一枪毙命，最强单发武器", "cons": "极贵，移速慢，击杀奖励低",
    },
    "FAMAS": {
        "price": 2050, "side": "CT", "type": "步枪",
        "damage": {"head": 140, "chest": 30, "stomach": 38, "leg": 23},
        "armor_pen": 70, "mag_size": 25, "fire_rate": 800,
        "reload_time": 3.3, "kill_reward": 300,
        "pros": "价格便宜，射速快，有burst模式", "cons": "伤害偏低，弹匣小",
    },
    "Galil AR": {
        "price": 2000, "side": "T", "type": "步枪",
        "damage": {"head": 140, "chest": 30, "stomach": 37, "leg": 23},
        "armor_pen": 70, "mag_size": 35, "fire_rate": 666,
        "reload_time": 3.0, "kill_reward": 300,
        "pros": "35发弹匣，性价比高", "cons": "伤害偏低，精度一般",
    },
    "SG 553": {
        "price": 3000, "side": "T", "type": "步枪",
        "damage": {"head": 140, "chest": 33, "stomach": 41, "leg": 25},
        "armor_pen": 100, "mag_size": 30, "fire_rate": 666,
        "reload_time": 3.0, "kill_reward": 300,
        "pros": "100%穿甲，带瞄准镜，后坐力小", "cons": "价格较高，开镜移速慢",
    },
    "AUG": {
        "price": 3300, "side": "CT", "type": "步枪",
        "damage": {"head": 140, "chest": 30, "stomach": 38, "leg": 23},
        "armor_pen": 90, "mag_size": 30, "fire_rate": 666,
        "reload_time": 3.3, "kill_reward": 300,
        "pros": "带瞄准镜，后坐力极小，精度高", "cons": "价格偏高（$3,300），伤害偏低",
    },
    "Desert Eagle": {
        "price": 700, "side": "both", "type": "手枪",
        "damage": {"head": 250, "chest": 63, "stomach": 78, "leg": 47},
        "armor_pen": 93, "mag_size": 7, "fire_rate": 266,
        "reload_time": 2.2, "kill_reward": 300,
        "pros": "一枪爆头必杀，便宜", "cons": "后坐力极大，射速慢，弹匣小",
    },
    "USP-S": {
        "price": 0, "side": "CT", "type": "手枪",
        "damage": {"head": 140, "chest": 35, "stomach": 44, "leg": 26},
        "armor_pen": 50.5, "mag_size": 12, "fire_rate": 352,
        "reload_time": 2.2, "kill_reward": 300,
        "pros": "免费，消音器，远距离精度极高", "cons": "有头盔时一枪爆头不死",
    },
    "Glock-18": {
        "price": 0, "side": "T", "type": "手枪",
        "damage": {"head": 115, "chest": 26, "stomach": 33, "leg": 20},
        "armor_pen": 47.5, "mag_size": 20, "fire_rate": 400,
        "reload_time": 2.2, "kill_reward": 300,
        "pros": "免费，20发弹匣，burst模式爆发高", "cons": "伤害低，穿甲率低",
    },
    "P250": {
        "price": 300, "side": "both", "type": "手枪",
        "damage": {"head": 140, "chest": 35, "stomach": 44, "leg": 26},
        "armor_pen": 73, "mag_size": 13, "fire_rate": 400,
        "reload_time": 2.2, "kill_reward": 300,
        "pros": "极便宜，性价比极高", "cons": "伤害不如 Deagle",
    },
    "MAC-10": {
        "price": 1050, "side": "T", "type": "冲锋枪",
        "damage": {"head": 127, "chest": 29, "stomach": 36, "leg": 22},
        "armor_pen": 61.5, "mag_size": 32, "fire_rate": 800,
        "reload_time": 2.1, "kill_reward": 600,
        "pros": "极便宜，射速快，击杀奖励高", "cons": "伤害低，穿甲率低",
    },
    "MP9": {
        "price": 1250, "side": "CT", "type": "冲锋枪",
        "damage": {"head": 115, "chest": 26, "stomach": 33, "leg": 20},
        "armor_pen": 60, "mag_size": 30, "fire_rate": 857,
        "reload_time": 2.1, "kill_reward": 600,
        "pros": "极快射速，跑射好，击杀奖励高", "cons": "伤害低，穿甲率低",
    },
    "P90": {
        "price": 2350, "side": "both", "type": "冲锋枪",
        "damage": {"head": 115, "chest": 26, "stomach": 33, "leg": 20},
        "armor_pen": 65, "mag_size": 50, "fire_rate": 857,
        "reload_time": 3.3, "kill_reward": 300,
        "pros": "50发超大弹匣，跑射极准", "cons": "伤害偏低，价格偏高",
    },
    "MAG-7": {
        "price": 1300, "side": "CT", "type": "霰弹枪",
        "damage": {"head": 120, "chest": 30, "stomach": 38, "leg": 23},
        "armor_pen": 50, "mag_size": 5, "fire_rate": 71,
        "reload_time": 2.5, "kill_reward": 900,
        "pros": "极近距离一发必杀，击杀奖励高", "cons": "弹匣仅5发，远距离无力",
    },
    "SSG 08": {
        "price": 1700, "side": "both", "type": "狙击步枪",
        "damage": {"head": 220, "chest": 88, "stomach": 110, "leg": 66},
        "armor_pen": 85, "mag_size": 10, "fire_rate": 48,
        "reload_time": 2.5, "kill_reward": 300,
        "pros": "便宜，轻便，一枪爆头必杀", "cons": "身体一枪不死，需要精准度",
    },
}


def compare_weapons(weapon_names: List[str]) -> str:
    """比较多把武器的参数

    Args:
        weapon_names: 武器名称列表，如 ["AK-47", "M4A4"]

    Returns:
        对比结果文本
    """
    valid_weapons = [w for w in weapon_names if w in WEAPON_STATS]
    if not valid_weapons:
        available = ", ".join(sorted(WEAPON_STATS.keys()))
        return f"未找到匹配的武器。可用武器：{available}"

    if len(valid_weapons) == 1:
        w = valid_weapons[0]
        s = WEAPON_STATS[w]
        return (
            f"【{w}】详细参数\n"
            f"价格：${s['price']} | 所属阵营：{s['side']} | 类型：{s['type']}\n"
            f"伤害：头部 {s['damage']['head']} | 胸部 {s['damage']['chest']} | 腹部 {s['damage']['stomach']} | 腿部 {s['damage']['leg']}\n"
            f"穿甲率：{s['armor_pen']}%\n"
            f"弹匣：{s['mag_size']} 发 | 射速：{s['fire_rate']} RPM | 换弹：{s['reload_time']}s\n"
            f"击杀奖励：${s['kill_reward']}\n"
            f"优点：{s['pros']}\n"
            f"缺点：{s['cons']}"
        )

    # 多武器对比
    lines = [f"【{', '.join(valid_weapons)}】参数对比\n"]
    headers = ["武器", "价格", "头部伤害", "胸部伤害", "穿甲率", "弹匣", "射速", "击杀奖励"]
    rows = []
    for w in valid_weapons:
        s = WEAPON_STATS[w]
        rows.append([
            w, f"${s['price']}", str(s['damage']['head']), str(s['damage']['chest']),
            f"{s['armor_pen']}%", f"{s['mag_size']}发", f"{s['fire_rate']}RPM", f"${s['kill_reward']}"
        ])

    # 格式化表格
    col_widths = [max(len(str(r[i])) for r in rows + [headers]) for i in range(len(headers))]
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep = "-" * len(header_line)
    lines.append(header_line)
    lines.append(sep)
    for row in rows:
        lines.append(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))

    # 总结建议
    lines.append("")
    lines.append("【购买建议】")
    for w in valid_weapons:
        s = WEAPON_STATS[w]
        lines.append(f"- {w}（${s['price']}）：{s['pros']}")

    return "\n".join(lines)


def recommend_weapon(budget: int, side: str, play_style: str = "all_round") -> str:
    """根据预算和阵营推荐武器

    Args:
        budget: 可用金钱
        side: "T" 或 "CT"
        play_style: "long_range", "close_range", "eco", "all_round"

    Returns:
        推荐结果
    """
    # 筛选可用武器
    available = {}
    for name, stats in WEAPON_STATS.items():
        if stats["price"] > budget:
            continue
        if side == "T" and stats["side"] == "CT":
            continue
        if side == "CT" and stats["side"] == "T":
            continue
        available[name] = stats

    if not available:
        return f"预算 ${budget} 不够买任何武器，建议只买手枪或 Eco。"

    # 按风格推荐
    if play_style == "long_range":
        priority = ["AWP", "SG 553", "AUG", "SSG 08", "AK-47", "M4A1-S", "M4A4", "Desert Eagle"]
    elif play_style == "close_range":
        priority = ["P90", "MAC-10", "MP9", "MAG-7", "MP7", "XM1014", "AK-47", "M4A4"]
    elif play_style == "eco":
        priority = ["MAC-10", "MP9", "FAMAS", "Galil AR", "Desert Eagle", "P250", "MAG-7", "MP7"]
    else:
        priority = ["AK-47", "M4A4", "M4A1-S", "AWP", "SG 553", "AUG", "FAMAS", "Galil AR"]

    for weapon in priority:
        if weapon in available:
            s = available[weapon]
            return (
                f"推荐：{weapon}（${s['price']}）\n"
                f"理由：{s['pros']}\n"
                f"剩余预算：${budget - s['price']}\n"
                f"建议购买：{weapon} + 头盔+防弹衣（$1,000）+ 道具"
            )

    return f"可用武器：{', '.join(sorted(available.keys()))}"


# 工具注册信息
TOOL_META = {
    "name": "weapon_comparer",
    "description": "对比 CS2 武器参数或根据预算推荐武器。输入武器名称列表可对比，或输入预算+阵营推荐武器。",
    "parameters": {
        "weapon_names": "要对比的武器名称列表，如 ['AK-47', 'M4A4']",
        "budget": "可用预算（推荐模式），如 4000",
        "side": "阵营（推荐模式）：T 或 CT",
        "play_style": "打法风格：long_range/close_range/eco/all_round",
    },
}
"""经济计算器工具：计算经济状况、推荐购买策略"""

from typing import Dict, Optional
from knowledge_base.data.economy import ECONOMY_CONSTANTS
from knowledge_base.data.weapons import WEAPON_BUILDS
from langchain_core.tools import tool


@tool
def calculate_team_economy(
    team: str,
    current_money: int,
    round_number: int,
    consecutive_losses: int,
    planted_c4: bool = False,
    won_last_round: bool = False,
) -> Dict:
    """计算团队经济状况并给出建议

    Args:
        team: "T" 或 "CT"
        current_money: 当前金钱
        round_number: 当前回合数（1-24）
        consecutive_losses: 连续输局数
        planted_c4: T 侧是否安装了 C4
        won_last_round: 上一局是否赢了

    Returns:
        经济分析结果
    """
    # 计算下局收入
    loss_bonus_list = ECONOMY_CONSTANTS["loss_bonus"]
    next_loss_bonus = loss_bonus_list[min(consecutive_losses, 5)]
    c4_bonus = ECONOMY_CONSTANTS["c4_plant_bonus"] if planted_c4 and team == "T" else 0

    # 下局最低收入
    next_round_income = next_loss_bonus + c4_bonus
    next_round_money = current_money + next_round_income

    # 计算下局可买装备
    armor_cost = 1000  # 头盔+防弹衣
    rifle_cost_t = 2700  # AK-47
    rifle_cost_ct = 3100  # M4A4
    pistol_armor_cost = 700 + 1000  # Desert Eagle + 全甲

    # 判断经济状态
    if won_last_round:
        if current_money >= 4000:
            state = "full_buy"
            advice = "可以 Full Buy 全队起步枪+全甲+道具"
        elif current_money >= 2000:
            state = "half_buy"
            advice = "半起局，建议买冲锋枪或手枪+半甲"
        else:
            state = "eco"
            advice = "手枪局后经济不足，建议 Eco 存钱"
    else:
        if next_round_money >= 4000:
            state = "full_buy"
            advice = f"下局有 ${round(next_round_money)}，可以 Full Buy"
        elif next_round_money >= 2000:
            state = "force_buy"
            advice = f"下局有 ${round(next_round_money)}，建议半起或强起"
        else:
            state = "eco"
            advice = f"下局只有 ${round(next_round_money)}，建议 Eco 存钱"

    # 详细建议
    if team == "T":
        if next_round_money >= 4700:
            specific = "AK-47 + 全甲 + 道具（烟雾弹+闪光弹+燃烧弹）"
        elif next_round_money >= 3700:
            specific = "AK-47 + 全甲 或 Galil AR + 全甲 + 道具"
        elif next_round_money >= 2700:
            specific = "Galil AR + 半甲 + 道具 或 Desert Eagle + 全甲 + 道具"
        elif next_round_money >= 1750:
            specific = "MAC-10 + 半甲 + 道具 或 Tec-9 + 全甲 + 道具"
        else:
            specific = "Eco 存钱，只买手枪或 P250"
    else:
        if next_round_money >= 5100:
            specific = "M4A4/M4A1-S + 全甲 + 拆弹器 + 道具"
        elif next_round_money >= 4100:
            specific = "M4A4/M4A1-S + 全甲 + 拆弹器 或 FAMAS + 全甲 + 道具"
        elif next_round_money >= 3000:
            specific = "FAMAS + 全甲 + 拆弹器 或 MP9 + 全甲 + 道具"
        elif next_round_money >= 2000:
            specific = "MP9 + 半甲 + 道具 或 MAG-7 + 半甲（B 点防守）"
        else:
            specific = "Eco 存钱，Five-SeveN + 道具 或 P250"

    # 根据回合数的特殊建议
    round_advice = ""
    if round_number >= 15 and round_number <= 16:
        round_advice = "换边后经济重置，建议根据当前金钱稳健购买"
    if round_number == 24 or round_number == 12:
        round_advice = "上半场/下半场最后一局，不考虑经济，可以全买"

    return {
        "team": team,
        "current_money": current_money,
        "next_round_money": round(next_round_money),
        "state": state,
        "state_label": {
            "full_buy": "Full Buy（强起局）",
            "half_buy": "Half Buy（半起局）",
            "force_buy": "Force Buy（强起局）",
            "eco": "Eco（经济局）",
        }.get(state, state),
        "advice": advice,
        "specific_equipment": specific,
        "round_advice": round_advice,
        "consecutive_losses": consecutive_losses,
        "next_loss_bonus": next_loss_bonus,
        "c4_bonus": c4_bonus,
    }


@tool
def get_eco_strategy(team: str, round_number: int, score_t: int, score_ct: int) -> str:
    """根据比分和回合数给出经济策略建议"""
    is_match_point = (team == "T" and score_t >= 12) or (team == "CT" and score_ct >= 12)
    is_critical_round = round_number in [1, 2, 3, 12, 15, 16, 24]

    if round_number == 1:
        return "手枪局：T 买 Glock + 道具（烟雾弹+闪光弹）或 P250 升级。CT 买 USPS + 防弹衣或道具。"

    if is_match_point:
        return "赛点局！不考虑经济，全队必须 Full Buy 或强起，输了就结束了。"

    if round_number == 12:
        return "上半场最后一局，不考虑存钱，全队可以花光所有钱。"

    if round_number == 24:
        return "下半场最后一局，不考虑存钱，全队可以花光所有钱。"

    if team == "T":
        return "T 侧标准经济循环：赢局 → 继续 Full Buy → 输局 → Eco 1-2 局 → 攒钱 Full Buy"
    else:
        return "CT 侧标准经济循环：赢局 → 继续 Full Buy → 输局 → Eco 1-2 局 → 攒钱 Full Buy"


def calculate_equipment_cost(items: list) -> Dict:
    """计算装备总花费"""
    prices = {
        "ak47": 2700, "m4a4": 3100, "m4a1s": 3100, "awp": 4750,
        "famas": 2050, "galil": 2000, "sg553": 3000, "aug": 3300,
        "mac10": 1050, "mp9": 1250, "mp7": 1500, "p90": 2350,
        "deagle": 700, "p250": 300, "fiveseven": 500, "tec9": 500,
        "cz75": 500, "usp": 0, "glock": 0,
        "kevlar": 650, "helmet": 350, "kevlar+helmet": 1000,
        "smoke": 300, "flash": 200, "he": 300, "molotov": 600, "incendiary": 600,
        "defuse_kit": 400, "decoy": 50,
    }
    total = 0
    details = []
    for item in items:
        key = item.lower().replace("-", "").replace(" ", "").replace("_", "")
        if key in prices:
            price = prices[key]
            total += price
            details.append(f"{item}: ${price}")
        else:
            details.append(f"{item}: 价格未知")
    return {
        "total": total,
        "details": details,
        "remaining": 800 - total if total <= 800 else f"超出 ${total - 800}（需要额外金钱）",
    }


# 工具注册信息
TOOL_META = {
    "name": "economy_calculator",
    "description": "计算 CS2 经济状况，给出购买建议。输入队伍（T/CT）、当前金钱、连续输局数等，返回经济分析和推荐装备。",
    "parameters": {
        "team": "队伍阵营：T 或 CT",
        "current_money": "当前金钱数",
        "round_number": "当前回合数",
        "consecutive_losses": "连续输局数",
        "planted_c4": "是否安装了 C4（T 侧）",
        "won_last_round": "上一局是否赢了",
    },
}
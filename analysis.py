""" 数据分析 + LLM Prompt 构建 """

from collections import defaultdict

from config import WEAPON_CATS, WEAPON_NAMES


def clean_weapon(w):
    return WEAPON_NAMES.get(w, w.replace("_", " ").title())


def build_coach_data(data, player_sid):
    """从原始解析数据中提取教练分析特征."""
    kp = data["kill_positions"]
    my_kills = [k for k in kp if k["killer_sid"] == player_sid]
    my_deaths = [k for k in kp if k["victim_sid"] == player_sid]
    p = data["player_stats"].get(player_sid, {})

    wb = defaultdict(lambda: {"kills": 0, "hs": 0, "dist": 0})
    for k in my_kills:
        wb[k["weapon"]]["kills"] += 1
        wb[k["weapon"]]["hs"] += 1 if k["headshot"] else 0
        wb[k["weapon"]]["dist"] += k["distance"]
    for k in my_deaths:
        wb[k["weapon"]]["deaths"] = wb[k["weapon"]].get("deaths", 0) + 1

    weapon_analysis = []
    for w, s in sorted(wb.items(), key=lambda x: x[1]["kills"], reverse=True):
        weapon_analysis.append({
            "weapon": clean_weapon(w),
            "category": WEAPON_CATS.get(w, "其他"),
            "kills": s["kills"],
            "deaths": s.get("deaths", 0),
            "hs_pct": round(s["hs"] / max(s["kills"], 1) * 100, 1),
            "avg_dist": round(s["dist"] / max(s["kills"], 1), 1),
        })

    dists = [k["distance"] for k in my_kills]
    cat_hs = defaultdict(lambda: {"kills": 0, "hs": 0})
    for k in my_kills:
        c = WEAPON_CATS.get(k["weapon"], "其他")
        cat_hs[c]["kills"] += 1
        if k["headshot"]:
            cat_hs[c]["hs"] += 1

    return {
        "name": p.get("name", "?"),
        "kills": p.get("kills", 0),
        "deaths": p.get("deaths", 0),
        "kd": p.get("kd", 0),
        "hs_pct": p.get("hs_pct", 0),
        "weapon_analysis": weapon_analysis,
        "cat_hs": [{"cat": c, "kills": s["kills"],
                     "hs_pct": round(s["hs"] / max(s["kills"], 1) * 100, 1)}
                   for c, s in sorted(cat_hs.items(),
                                      key=lambda x: x[1]["kills"], reverse=True)],
        "avg_kill_dist": round(sum(dists) / max(len(dists), 1), 1) if dists else 0,
        "close": sum(1 for d in dists if d < 10),
        "mid": sum(1 for d in dists if 10 <= d < 25),
        "long": sum(1 for d in dists if d >= 25),
        "utility_kills": sum(1 for k in my_kills
                             if k["weapon"] in ("hegrenade", "incgrenade", "molotov")),
        "top_weapon": weapon_analysis[0]["weapon"] if weapon_analysis else "无",
        "top_weapon_kills": weapon_analysis[0]["kills"] if weapon_analysis else 0,
    }


def build_prompt(d):
    """构建发送给 LLM 的教练分析 Prompt."""
    wa = "\n".join(
        f"  {w['weapon']}: {w['kills']}杀/爆头率{w['hs_pct']}%/平均{w['avg_dist']}m"
        for w in d["weapon_analysis"][:10]
    )
    ch = "\n".join(
        f"  {c['cat']}: {c['kills']}杀/爆头率{c['hs_pct']}%"
        for c in d["cat_hs"]
    )

    utils_note = f"道具击杀: {d['utility_kills']}次"

    return f"""你是一个严厉但专业的 CS2 教练。请分析以下选手数据，给出具体的训练建议。

## 选手数据
- 击杀: {d['kills']} | 死亡: {d['deaths']} | K/D: {d['kd']}
- 爆头率: {d['hs_pct']}%
- 平均击杀距离: {d['avg_kill_dist']}m
- 近战 {d['close']} | 中程 {d['mid']} | 远程 {d['long']}
- {utils_note}
- 最强武器: {d['top_weapon']} ({d['top_weapon_kills']}杀)

## 武器详情
{wa}

## 按类别爆头率
{ch}

## 分析要求
从以下 5 个维度分析，每点都要有数据支撑 + 具体训练建议：
1. 枪法与预瞄
2. 走位与位置感
3. 武器选择
4. 道具使用
5. 综合训练计划（30分钟/1小时/2小时 三档）

用中文回答，语气要像真正的教练一样有说服力。"""


def build_clutch_data(round_data, player_name):
    """从回合数据中检测残局回合."""
    clutches = []
    for r, rd in sorted(round_data.items()):
        seq = rd["kill_seq"]
        # 找本玩家击杀最多的回合
        my_kills = [k for k in seq if k["killer"] == player_name]
        other_kills = [k for k in seq if k["killer"] != player_name and k["killer"] != k["victim"]]
        my_deaths = [k for k in seq if k["victim"] == player_name]

        if my_kills and len(my_deaths) == 0 and len(my_kills) >= 2:
            # 多杀且没死 — 可能是残局
            clutches.append({
                "round": r,
                "my_kills": len(my_kills),
                "total_kills": rd["kills"],
                "summary": " → ".join(
                    f"{k['killer']} {k['weapon']} {k['victim']}{" (HS)" if k['headshot'] else ''}"
                    for k in seq
                ),
            })

    return clutches[:5]  # 最多返回 5 个


def build_round_summary(round_data, player_name, limit=10):
    """构建最近回合摘要."""
    lines = []
    for r in sorted(round_data.keys())[-limit:]:
        rd = round_data[r]
        my_kills = [k for k in rd["kill_seq"] if k["killer"] == player_name]
        my_deaths = [k for k in rd["kill_seq"] if k["victim"] == player_name]
        lines.append(
            f"回合{r}: {rd['kills']}个击杀, "
            f"你 {'杀'+str(len(my_kills))+'个' if my_kills else '0杀'} / "
            f"{'死'+str(len(my_deaths))+'次' if my_deaths else '存活'}"
        )
    return "\n".join(lines)


def build_system_prompt(coach_data, history_text="", round_data=None, player_name=""):
    """构建对话模式的 System Prompt."""
    wa = "\n".join(
        f"- {w['weapon']}: {w['kills']}杀/爆头率{w['hs_pct']}%/平均{w['avg_dist']}m"
        for w in coach_data["weapon_analysis"][:8]
    )

    # 回合摘要
    round_text = ""
    clutch_text = ""
    if round_data:
        round_text = build_round_summary(round_data, player_name, limit=10)
        clutches = build_clutch_data(round_data, player_name)
        if clutches:
            clutch_lines = [f"  第{c['round']}回合: {c['my_kills']}杀 ({c['summary']})" for c in clutches]
            clutch_text = "\n".join(clutch_lines)

    clutch_section = f"""
## 残局回合记录
{clutch_text}
""" if clutch_text else ""

    round_section = f"""
## 最近回合摘要
{round_text}
""" if round_text else ""

    return f"""你是 CS2 专业教练，正在分析玩家 "{coach_data['name']}" 的数据。
语气严厉但靠谱，回答简洁有数据支撑。

当前数据:
- K/D {coach_data['kd']} | HS% {coach_data['hs_pct']}%
- 主武器: {coach_data['top_weapon']} ({coach_data['top_weapon_kills']}杀)

{wa}
{round_section}
{clutch_section}
{history_text}

回答要求:
1. 用数据说话
2. 对比历史记录
3. 你的回复可引用具体回合数据，比如 "第3回合你..."
4. 结尾给训练建议
5. 不知道就说不知道"""
